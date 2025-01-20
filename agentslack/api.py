from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from agentslack.Slack import Slack
from agentslack.registry import Registry
import threading
import uvicorn
import time
from agentslack.types import Message, Channel


class Tool(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class WorldRegistration(BaseModel):
    world_name: str

class AgentRegistration(BaseModel):
    agent_name: str
    world_name: str

class Server:
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.app = FastAPI()
        self.host = host
        self.port = port
        self.registry = Registry()
        self.tools = {
            "send_dm": Tool(
                name="send_dm",
                description="Send a message to a user",
                parameters={
                    "your_name": "string",
                    "recipient_name": "string",
                    "message": "string",
                }
            ),
            "send_broadcast": Tool(
                name="send_broadcast",
                description="Send a message to a channel",
                parameters={
                    "your_name": "string",
                    "channel_name": "string",
                    "message": "string",
                }
            ),
            "read_dm": Tool(
                name="read_dm",
                description="Read a direct message",
                parameters={
                    "your_name": "string",
                    "sender_name": "string",
                }
            ),
            "check_new_messages": Tool(
                name="check_new_messages",
                description="Check if there are new messages across all channels and dms",
                parameters={
                    "your_name": "string"
                }
            ),
            "read_channel": Tool(
                name="read_channel",
                description="Read a channel",
                parameters={
                    "your_name": "string",
                    "channel_name": "string",
                }
            ),
            "list_channels": Tool(
                name="list_all_my_channels",
                description="List all channels I have access to",
                parameters={
                    "agent_name": "string"
                }
            ),
            "create_channel": Tool(
                name="create_channel",
                description="Create a new channel",
                parameters={
                    "your_name": "string",
                    "channel_name": "string",
                }
            )
        }
        self.server_thread = None
        self._setup_routes()

    def only_show_new_messages(self, agent_name: str, channel_id: str, messages: List[Message]) -> List[Message]:
        # filter based on messages the agent has already seen
        # take in a new list of messages from a channel
        # filter the messages that were not in the previous agent set of messages
        # return the new messages
        agent = self.registry.get_agent(agent_name)
        
        previous_messages = agent.read_messages.get(channel_id, [])
        print(f"[DEBUG] Previous messages: {previous_messages}")
        new_messages = [msg for msg in messages if msg not in previous_messages]
        return new_messages
    
    def update_channels(self, agent_name: str) -> None:
        agent = self.registry.get_agent(agent_name)
        # Get ongoing DMs and regular channels
        ongoing_dms = agent.slack_client.check_ongoing_dms()
        channels = agent.slack_client.list_channels()
        # Combine both DMs and regular channels
        all_channels = []
        existing_channel_ids = set()
        
        if ongoing_dms.get('channels'):
            for channel in ongoing_dms['channels']:
                if channel['id'] not in existing_channel_ids:
                    all_channels.append(Channel(slack_id=channel['id'], name="dm"))
                    existing_channel_ids.add(channel['id'])
                    
        if channels.get('channels'):
            for channel in channels['channels']:
                if channel['id'] not in existing_channel_ids:
                    all_channels.append(Channel(slack_id=channel['id'], name=channel['name']))
                    existing_channel_ids.add(channel['id'])
            
        # Update agent's channels with the combined list
        agent.channels = all_channels

    def _update_agent_read_messages(self, agent_name: str, channel_id: str, messages: List[Message]) -> None:
        agent = self.registry.get_agent(agent_name)
        # append any message in messages that's not already in the agent's read_messages
        agent.read_messages[channel_id].extend([message for message in messages if message not in agent.read_messages[channel_id]])


    def _setup_routes(self):
        @self.app.get("/tools")
        async def list_tools():
            return list(self.tools.values())
            
        @self.app.post("/tools/{tool_name}")
        async def call_tool(tool_name: str, parameters: Dict[str, Any]):
            if tool_name not in self.tools:
                raise HTTPException(status_code=404, detail="Tool not found")
                
            if tool_name == "send_dm":
                print("PARAMETERS", parameters)
                slack_client = self.registry.get_agent(parameters["your_name"]).slack_client
                id_of_recipient = self.registry.get_agent(parameters["recipient_name"]).slack_app.slack_id
                
                response = slack_client.open_conversation(user_ids=[id_of_recipient])
                if response['ok']:
                    channel_id = response['channel']['id']
                else:
                    raise HTTPException(status_code=400, detail="Failed to open conversation")

                response = slack_client.send_messsage(
                    message=parameters["message"],
                    target_channel_id=channel_id
                )
                # update the agent's channel with this message
                self._update_agent_read_messages(parameters["your_name"], channel_id, [Message(message=parameters["message"], channel_id=channel_id, user_id=parameters["your_name"], timestamp=time.time(), agent_name=parameters["your_name"])])
                return str(response)
            
            elif tool_name == "send_broadcast":
                # send message to a channel 
                slack_client = self.registry.get_agent(parameters["your_name"]).slack_client
                channel_name = parameters["channel_name"]
                channels = self.registry.get_agent(parameters["your_name"]).channels
                channel_names = [channel.name for channel in channels]
                if channel_name not in channel_names:
                    response = "sorry this channel doesn't exist"
                    # TODO feature coming soon 
                else: 
                    channel_id = self.registry.get_channel(channel_name).slack_id
                    response = slack_client.send_messsage(
                        message=parameters["message"],
                        target_channel_id=channel_id
                    )
                return str(response)

            elif tool_name == "list_channels":
                slack_client = self.registry.get_agent(parameters["your_name"]).slack_client
                response = slack_client.list_channels()
                return response['channels']
            
            elif tool_name == "read_channel":
                slack_client = self.registry.get_agent(parameters["your_name"]).slack_client
                channel_id = self.registry.get_channel(parameters["channel_name"]).slack_id
                response = slack_client.read(channel_id=channel_id)
                agent = self.registry.get_agent(parameters["your_name"])
                world_start_datetime = self.registry.get_world(agent.world_name).start_datetime
                # restrict to messages after the world start datetime 
                messages = response['messages']
                messages = [msg for msg in messages if msg['ts'] > world_start_datetime]
                messages = [Message(message=message['text'], channel_id=channel_id, user_id=message['user'], timestamp=message['ts']) for message in messages]
                # update the agent's channel with these messages
                self._update_agent_read_messages(parameters["your_name"], channel_id, messages)
                return messages
            
            elif tool_name == "read_dm":
                # DMs for now are only between two agents (plus humans)
                total_users = len(self.registry.get_humans()) + 2

                # get the main agent 
                slack_client = self.registry.get_agent(parameters["your_name"]).slack_client
                sender_name = parameters["sender_name"]

                # get the ids, needed for communication with slack 
                sender_agent = self.registry.get_agent(sender_name)
                sender_id = sender_agent.slack_app.slack_id

                receiver_id = self.registry.get_agent(parameters["your_name"]).slack_app.slack_id
                # loop over channels from the agent 
                channels = slack_client.check_ongoing_dms()
                for channel in channels['channels']:
                    members = slack_client.get_channel_members(channel['id'])['members']
                    if len(members) == total_users:
                        # make sure both the sender and receiver are in the channel 
                        if (sender_id in members) and (receiver_id in members):
                            channel_id = channel['id']
                            break
                response = slack_client.read(channel_id=channel_id)
                
                self._update_agent_read_messages(parameters["your_name"], channel_id, response['messages'])

                messages = response['messages']
                world_start_datetime = self.registry.get_world(sender_agent.world_name).start_datetime
                # restrict to messages after the world start datetime 
                messages = [msg for msg in messages if msg['ts'] >= world_start_datetime]

                messages = [Message(message=message['text'], channel_id=channel_id, user_id=message['user'], timestamp=message['ts'], agent_name=self.registry.get_agent_name_from_id(message['user'])) for message in messages]

                # update the agent's channel with these messages
                self._update_agent_read_messages(parameters["your_name"], channel_id, messages)
                return messages
            
            elif tool_name == "check_ongoing_dms":
                response = self.slack.check_ongoing_dms()
                return response
            
            elif tool_name == "check_new_messages":
                # return all channels and dms the user is a part of 
                # ensure the timestamp of the messages is greater than 
                # the start of the world 
                agent = self.registry.get_agent(parameters["your_name"])
                agent_id = agent.slack_app.slack_id
                world_start_datetime = self.registry.get_world(agent.world_name).start_datetime
                print(f"[DEBUG] World start datetime: {world_start_datetime}")
                self.update_channels(parameters["your_name"])
                channels = agent.channels
                channel_ids = [channel.slack_id for channel in channels]

                channel_ids_with_agent = []
                for channel_id in channel_ids:
                    members = agent.slack_client.get_channel_members(channel_id)['members']
                    if agent_id in members:
                        channel_ids_with_agent.append(channel_id)

                all_new_messages = []
                print(f"[DEBUG] Channel IDs with agent: {channel_ids_with_agent}")
                for i, channel_id in enumerate(channel_ids_with_agent):
                    messages = agent.slack_client.read(channel_id)['messages']

                    # filter to make sure the messages are after the world start datetime
                    msgs_after = [msg for msg in messages if msg['ts'].split('.')[0] >= str(world_start_datetime)]

                    msgs_after = [Message(message=message['text'], channel_id=channel_id, user_id=message['user'], timestamp=message['ts'].split('.')[0], agent_name=self.registry.get_agent_name_from_id(message['user'])) for message in msgs_after]
                    if len(msgs_after) == 0:
                        continue
    
                    print(f"[DEBUG] All messages after conversion: {len(msgs_after)}")

                    # filter out messages that the agent has already seen
                    new_messages = self.only_show_new_messages(parameters["your_name"], channel_id, msgs_after)
                    print(f"[DEBUG] New messages after filtering: {len(new_messages)}")
                    all_new_messages.append(new_messages)
                    self._update_agent_read_messages(parameters["your_name"], channel_id, new_messages)
                return all_new_messages


            
            elif tool_name == "create_channel":
                slack_client = self.registry.get_agent(parameters["your_name"]).slack_client
                response = slack_client.create_channel(
                    channel_name=parameters["channel_name"],
                )
                return response
            
            elif tool_name == "add_user_to_channel":
                response = self.slack.add_user_to_channel(
                    channel_id=parameters["channel_id"],
                    user_id=parameters["user_id"]
                )
                return {"status": "success", "response": str(response)}
            
            elif tool_name == "open_conversation":
                response = self.slack.open_conversation(
                    user_ids=parameters["user_ids"]
                )
                return response

            raise HTTPException(status_code=400, detail="Tool execution failed")

        @self.app.post("/register_world")
        async def register_world(request: WorldRegistration):
            try:
                self.registry.register_world(request.world_name)
                return {"status": "success", "message": f"World {request.world_name} registered successfully"}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.app.post("/register_agent")
        async def register_agent(request: AgentRegistration):
            try:
                self.registry.register_agent(request.agent_name, request.world_name)
                return {"status": "success", "message": f"Agent {request.agent_name} registered successfully in world {request.world_name}"}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
    
    def start(self):
        """Start the server in a background thread"""
        if self.server_thread is not None:
            return  # Server already running
            
        def run_server():
            uvicorn.run(self.app, host=self.host, port=self.port)
            
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(1)  # Give the server a moment to start

    def stop(self):
        """Stop the server"""
        if self.server_thread is not None:
            self.server_thread.join(timeout=1)
            self.server_thread = None


if __name__ == "__main__":
    server = Server()
    server.start()
