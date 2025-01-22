import os 
import json 
from typing import Dict, Set, Optional, List 
from dataclasses import asdict
from datetime import datetime
from copy import deepcopy
from agentslack.Slack import Slack
from agentslack.types_ import Agent, Channel, World, Message, SlackApp, Human

class RegistryError(Exception):
    """Base exception for registry errors"""
    pass

class DuplicateAgentError(RegistryError):
    """Raised when trying to register an agent with a name that already exists"""
    pass

class DuplicateWorldError(RegistryError):
    """Raised when trying to register a world with a name that already exists"""
    pass


class Registry:
    def __init__(self):
        with open('slack_config.json', 'r') as file:
            self.slack_config = json.load(file)
            
        with open('config.json', 'r') as file:
            self.config = json.load(file)

        os.environ['SLACK_CLIENT_ID'] = self.slack_config['slack_client_id']
        os.environ['SLACK_CLIENT_SECRET'] = self.slack_config['slack_client_secret']

        self._world_name_mapping: Dict[str, World] = {} # world_name -> World
        self._agent_name_mapping: Dict[str, Agent] = {} # agent_name -> Agent

        self._channel_name_mapping: Dict[str, Channel] = {} # name -> Channel

        self._world_to_channels: Dict[str, List[str]] = {} # world_name -> channels
        self._channels_to_world: Dict[str, str] = {} # channel_id -> world_name

        self._agent_slack_clients: Dict[str, Slack] = {} # agent_name -> Slack

        self._world_to_dms: Dict[str, List[str]] = {} # world_name -> dms
        self._dms_to_world: Dict[str, str] = {} # dm_id -> world_name

        self._always_add_users: List[str] = self.slack_config['always_add_users'] + [self.slack_config['slack_app_info']['world_app']['slack_member_id']]

        self._humans: List[Human] = [Human(slack_member_id=human['slack_member_id'], name=human['name'], expertise=human['expertise']) for human in self.slack_config['humans']]
        
        self.world_client = Slack(slack_token=self.slack_config['slack_app_info']['world_app']['slack_token'], always_add_users=self._always_add_users)
        self.world_token = self.slack_config['slack_app_info']['world_app']['slack_token']


        self._slack_apps: List[SlackApp] = [SlackApp(slack_token=app['slack_token'], slack_id=app['slack_member_id']) for app in  self.slack_config['slack_app_info']['agent_apps']]
        self._agent_app_mapping: Dict[str, str] = {} # agent_name -> slack_app_id
        self._app_agent_mapping: Dict[str, str] = {} # slack_app_id -> agent_name
        
    def register_world(self, world_name: str) -> None:
        """Register a new world. Raises DuplicateWorldError if name already exists."""
        if world_name in self._world_name_mapping:
            raise DuplicateWorldError(f"World '{world_name}' already exists")
        self._world_name_mapping[world_name] = World(start_datetime=datetime.now().timestamp())

        self._world_name_mapping[world_name].slack_client = self.world_client
        # create a world channel, akin to a public space 
        # add all the channels to the world 
        channels = self.world_client.list_channels()
        # print(channels)
        for channel in channels['channels']:
            self._world_name_mapping[world_name].channels.append(Channel(slack_id=channel['id'], name=channel['name']))
            self._channel_name_mapping[channel['name']] = Channel(slack_id=channel['id'], name=channel['name'])
            
    def register_agent(self, agent_name: str, world_name: str) -> None:
        """Register a new agent. Raises DuplicateAgentError if name already exists."""
        if agent_name in self._agent_name_mapping:
            raise DuplicateAgentError(f"Agent '{agent_name}' already exists")
            
        # Create world if it doesn't exist
        if world_name not in self._world_name_mapping:
            self.register_world(world_name)
            
        self._world_name_mapping[world_name].agents.add(agent_name)

        num_agents = len(self._agent_name_mapping)
        if num_agents >= len(self._slack_apps):
            raise RegistryError("No more slack apps available")
        
        new_app = self._slack_apps[num_agents]

        self._agent_slack_clients[agent_name] = Slack(slack_token=new_app.slack_token, always_add_users=self._always_add_users)

        self._agent_name_mapping[agent_name] = Agent(world_name=world_name, 
                                                     agent_name=agent_name,
                                                     slack_app=new_app, 
                                                     slack_client=self._agent_slack_clients[agent_name],
                                                     channels=self._world_name_mapping[world_name].channels)
        
        # TODO: change this so we don't have to do so many calls to slack 
        # e.g., sometimes the user is already in the channel.
        for channel in self._world_name_mapping[world_name].channels:
            self._agent_name_mapping[agent_name].slack_client.add_user_to_channel(channel.slack_id, [new_app.slack_id] + self._always_add_users)

        self._agent_app_mapping[agent_name] = new_app.slack_id
        self._app_agent_mapping[new_app.slack_id] = agent_name

    def get_agent_name_from_id(self, slack_app_id: str) -> str:
        return self._app_agent_mapping[slack_app_id]
    
    def get_humans(self) -> List[dict]:
        return [asdict(human) for human in self._humans]
    
    def get_human(self, human_name: str) -> Human:
        return next((human for human in self._humans if human.name == human_name), None)
    
    def get_world_starttime_of_agent(self, agent_name: str) -> str:
        return self._world_name_mapping[self._agent_name_mapping[agent_name].world_name].start_datetime

    def get_agent(self, agent_name: str) -> Agent:
        try: 
            return self._agent_name_mapping[agent_name]
        except KeyError:
            return f"Agent '{agent_name}' does not exist, here are possible agents: {self._agent_name_mapping.keys()}"
    
    def get_world(self, world_name: str) -> World:
        return self._world_name_mapping[world_name]

    def world_exists(self, world_name: str) -> bool:
        """Check if a world exists"""
        return world_name in self._worlds

    def agent_exists(self, agent_name: str) -> bool:
        """Check if an agent exists"""
        return agent_name in self._agents

    def register_human_in_world(self, world_name: str, human_id: str, slack_app_id: str) -> None:
        """Register a human in a world with their Slack user ID mapping"""
        if world_name not in self._worlds:
            self.register_world(world_name)
        world = self._worlds[world_name]
        world.humans.add(human_id)
        world.human_mappings[human_id] = slack_app_id

    def remove_human_from_world(self, world_name: str, human_id: str) -> None:
        if world_name in self._worlds:
            world = self._worlds[world_name]
            world.humans.discard(human_id)
            world.human_mappings.pop(human_id, None)
            
    def get_world_humans(self, world_name: str) -> Set[str]:
        return self._worlds.get(world_name, World()).humans
    
    def get_channel(self, channel_name: str) -> Channel:
        return self._channel_name_mapping[channel_name]
    
    def get_channel_from_id(self, channel_id: str) -> Channel:
        for agent in self._agent_name_mapping.keys():
            for channel in self._agent_name_mapping[agent].channels:
                if channel.slack_id == channel_id:
                    return channel
        return None
    
    def register_channel(self, agent_name: str, channel_name: str, channel_id: str) -> None:
        self._channel_name_mapping[channel_name] = Channel(slack_id=channel_id, name=channel_name)
        # get agent 
        agent = self._agent_name_mapping[agent_name]
        agent_world = agent.world_name
        self._world_name_mapping[agent_world].channels.append(Channel(slack_id=channel_id, name=channel_name))

    def is_human_in_world(self, world_name: str, human_id: str) -> bool:
        return human_id in self._worlds.get(world_name, World()).humans

    def exclude_human_from_agent(self, agent_name: str, human_id: str) -> None:
        """Prevent an agent from interacting with a specific human"""
        if agent_name in self._agents:
            self._agents[agent_name].excluded_humans.add(human_id)

    def include_human_for_agent(self, agent_name: str, human_id: str) -> None:
        """Allow an agent to interact with a previously excluded human"""
        if agent_name in self._agents:
            self._agents[agent_name].excluded_humans.discard(human_id)

    def can_agent_interact_with_human(self, agent_name: str, human_id: str) -> bool:
        """Check if an agent can interact with a human"""
        if agent_name not in self._agents:
            return False
        agent = self._agents[agent_name]
        return (self.is_human_in_world(agent.world_name, human_id) and 
                human_id not in agent.excluded_humans)
        
    def register_channel(self, agent_name: str, channel_id: str, channel_name: str) -> None:
        if agent_name in self._agent_name_mapping:
            self._agent_name_mapping[agent_name].channels.append(Channel(slack_id=channel_id, name=channel_name))
            
    def register_dm(self, agent_name: str, dm_id: str) -> None:
        if agent_name in self._agents:
            self._agents[agent_name].dms.add(dm_id)
            
    def register_tool(self, agent_name: str, tool_id: str) -> None:
        if agent_name in self._agents:
            self._agents[agent_name].tools.add(tool_id)
            
    def get_agent_world(self, agent_name: str) -> Optional[str]:
        if agent_name in self._agents:
            return self._agents[agent_name].world_name
        return None
    
    def get_always_add_users(self) -> List[str]:
        return self._always_add_users
        
    def get_world_agents(self, world_name: str) -> Set[str]:
        return self._worlds.get(world_name, World()).agents
    
    def get_all_agents(self) -> list[Agent]:
        return list(self._agent_name_mapping.values())
    
    def get_all_agent_names(self) -> list[str]:
        return list(self._agent_name_mapping.keys())
    
    def get_slack_app_id(self, agent_name: str, human_id: str) -> Optional[str]:
        """Get Slack user ID for a human if the agent can interact with them"""
        if agent_name in self._agents:
            if self.can_agent_interact_with_human(agent_name, human_id):
                agent = self._agents[agent_name]
                world = self._worlds.get(agent.world_name)
                if world:
                    return world.human_mappings.get(human_id)
        return None
        
        
    def get_masked_slack_config(self) -> dict:
        config = deepcopy(self.slack_config)
        
        for app in config['slack_app_info']['agent_apps']:
            app['slack_token'] = "********"
        config['slack_app_info']['world_app']['slack_token'] = "********"
        
        config['slack_client_secret'] = "********"
        config['slack_client_id'] = "********"
        return config
