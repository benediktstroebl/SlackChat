from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from agentslack.Slack import Slack
from agentslack.registry import Registry
import threading
import uvicorn
import time
from agentslack.types import Message
from dataclasses import asdict

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
    def __init__(self):
        self.app = FastAPI()
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

    @staticmethod
    def only_show_new_messages(agent_name: str, channel_id: str, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # filter based on messages the agent has already seen
        pass 
    
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
                print("TYPE OF RESPONSE", type(response))
                print("RAP GOD", response)
                messages = [asdict(Message(message=message['text'], channel_id=channel_id, user_id=message['user'], timestamp=message['ts'])) for message in response['messages']]
                # messages = self.only_show_new_messages(parameters["your_name"], channel_id, messages)
                return messages
            
            elif tool_name == "read_dm":
                total_users = len(self.registry.get_humans()) + 2

                print(self.registry.get_all_agents())

                slack_client = self.registry.get_agent(parameters["your_name"]).slack_client
                sender_name = parameters["sender_name"]
                sender_id = self.registry.get_agent(sender_name).slack_app.slack_id
                receiver_id = self.registry.get_agent(parameters["your_name"]).slack_app.slack_id
                # loop over channels from the agent 
                channels = slack_client.check_ongoing_dms()
                for channel in channels['channels']:
                    members = slack_client.get_channel_members(channel['id'])['members']
                    if len(members) == total_users:
                        if (sender_id in members) and (receiver_id in members):
                            

                            channel_id = channel['id']
                            break
                response = slack_client.read(channel_id=channel_id)

                messages = [asdict(Message(message=message['text'], channel_id=channel_id, user_id=message['user'], timestamp=message['ts'])) for message in response['messages']]
                # messages = self.only_show_new_messages(parameters["your_name"], channel_id, messages)
                return messages
            
            elif tool_name == "check_ongoing_dms":
                response = self.slack.check_ongoing_dms()
                return {"status": "success", "response": str(response)}
            
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
                return {"status": "success", "response": str(response)}

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
    
    def start(self, host: str = "0.0.0.0", port: int = 8080):
        """Start the server in a background thread"""
        if self.server_thread is not None:
            return  # Server already running
            
        def run_server():
            uvicorn.run(self.app, host=host, port=port)
            
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
