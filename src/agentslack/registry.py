import os 
import json 
from typing import Dict, Set, Optional, List 
from dataclasses import asdict
from datetime import datetime
from copy import deepcopy
from agentslack.Slack import Slack
from agentslack.validate import validate_configs
from agentslack.types import Agent, Channel, World, Message, SlackApp, Human

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

        self.always_return_messages = self.config['always_return_messages']
        assert self.always_return_messages in [True, False], "always_return_messages must be True or False"

        # Validate configs
        validate_configs(self.slack_config, self.config)

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
        self._human_id_mapping: Dict[str, Human] = {human.slack_member_id: human for human in self._humans}
        
        self.world_client = Slack(slack_token=self.slack_config['slack_app_info']['world_app']['slack_token'], always_add_users=self._always_add_users)
        self.world_token = self.slack_config['slack_app_info']['world_app']['slack_token']
        self.world_member_id = self.slack_config['slack_app_info']['world_app']['slack_member_id']

        self._slack_apps: List[SlackApp] = [SlackApp(slack_token=app['slack_token'], slack_id=app['slack_member_id']) for app in  self.slack_config['slack_app_info']['agent_apps']]
        self._agent_app_mapping: Dict[str, str] = {} # agent_name -> slack_app_id
        self._app_agent_mapping: Dict[str, str] = {} # slack_app_id -> agent_name
        
    def register_world(self, world_name: str) -> None:
        """Register a new world. Raises DuplicateWorldError if name already exists."""
        if world_name in self._world_name_mapping:
            raise DuplicateWorldError(f"World '{world_name}' already exists")
        self._world_name_mapping[world_name] = World(start_datetime=datetime.now().timestamp())
        self._world_name_mapping[world_name].slack_client = self.world_client
        # Each world starts with no channels - channels will be added as they are created
        self._world_name_mapping[world_name].channels = []

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

        self._agent_slack_clients[agent_name] = Slack(
            slack_token=new_app.slack_token, 
            always_add_users=self.get_always_add_users()
            )

        # Filter channels to only include ones from this world
        world_channels = []
        for channel in self._world_name_mapping[world_name].channels:
            if channel.slack_id in self._channels_to_world and self._channels_to_world[channel.slack_id] == world_name:
                world_channels.append(channel)

        self._agent_name_mapping[agent_name] = Agent(world_name=world_name, 
                                                     agent_name=agent_name,
                                                     slack_app=new_app, 
                                                     slack_client=self._agent_slack_clients[agent_name],
                                                     channels=world_channels)
        
        # TODO: change this so we don't have to do so many calls to slack 
        # e.g., sometimes the user is already in the channel.
        for channel in self._world_name_mapping[world_name].channels:
            self._agent_name_mapping[agent_name].slack_client.add_user_to_channel(
                channel.slack_id, [new_app.slack_id] + self.get_always_add_users())

        self._agent_app_mapping[agent_name] = new_app.slack_id
        self._app_agent_mapping[new_app.slack_id] = agent_name

    def get_agent_name_from_id(self, slack_app_id: str) -> str:
        return self._app_agent_mapping[slack_app_id]
    
    def get_agent_names(self) -> List[str]:
        return list(self._agent_name_mapping.keys())
    
    def name_from_any_id(self, user_id: str) -> str:
        if user_id in self._app_agent_mapping:
            return self._app_agent_mapping[user_id]
        for human in self._humans:
            if human.slack_member_id == user_id:
                return human.name
        return user_id

    def get_human_name_from_id(self, slack_app_id: str) -> str:
        for human in self._humans:
            if human.slack_member_id == slack_app_id:
                return human.name
        return None
    
    def get_humans(self) -> List[dict]:
        return [asdict(human) for human in self._humans]
    
    def get_human_names(self) -> List[str]:
        return [human.name for human in self._humans]
    
    def get_human(self, human_name: str) -> Human:
        return next((human for human in self._humans if human.name == human_name), None)

    def get_world_starttime_of_agent(self, agent_name: str) -> str:
        return self._world_name_mapping[self._agent_name_mapping[agent_name].world_name].start_datetime

    def get_agent(self, agent_name: str) -> Agent:
        return self._agent_name_mapping.get(agent_name, None)
    
    def get_world(self, world_name: str) -> World:
        return self._world_name_mapping[world_name]

    def world_exists(self, world_name: str) -> bool:
        """Check if a world exists"""
        return world_name in self._world_name_mapping

    def agent_exists(self, agent_name: str) -> bool:
        """Check if an agent exists"""
        return agent_name in self._agent_name_mapping
    
    def human_exists(self, human_name: str) -> bool:
        """Check if a human exists"""
        return human_name in self.get_human_names()

    def register_human_in_world(self, world_name: str, human_id: str, slack_app_id: str) -> None:
        """Register a human in a world with their Slack user ID mapping"""
        if world_name not in self._world_name_mapping:
            self.register_world(world_name)
        world = self._world_name_mapping[world_name]
        world.humans.add(human_id)
        world.human_mappings[human_id] = slack_app_id

    def remove_human_from_world(self, world_name: str, human_id: str) -> None:
        if world_name in self._world_name_mapping:
            world = self._world_name_mapping[world_name]
            world.humans.discard(human_id)
            world.human_mappings.pop(human_id, None)
            
    def get_world_humans(self, world_name: str) -> Set[str]:
        return self._world_name_mapping.get(world_name, World()).humans
    
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
        agent.channels.append(Channel(slack_id=channel_id, name=channel_name))
        # Track which world owns this channel
        self._channels_to_world[channel_id] = agent_world
        
        # Add always_add_users to the new channel
        agent.slack_client.add_user_to_channel(
            channel_id=channel_id,
            user_id=self.get_always_add_users()
        )

    def is_human_in_world(self, world_name: str, human_id: str) -> bool:
        return human_id in self._world_name_mapping.get(world_name, World()).humans

    def exclude_human_from_agent(self, agent_name: str, human_id: str) -> None:
        """Prevent an agent from interacting with a specific human"""
        if agent_name in self._agent_name_mapping:
            self._agent_name_mapping[agent_name].excluded_humans.add(human_id)

    def include_human_for_agent(self, agent_name: str, human_id: str) -> None:
        """Allow an agent to interact with a previously excluded human"""
        if agent_name in self._agent_name_mapping:
            self._agent_name_mapping[agent_name].excluded_humans.discard(human_id)

    def can_agent_interact_with_human(self, agent_name: str, human_id: str) -> bool:
        """Check if an agent can interact with a human"""
        if agent_name not in self._agent_name_mapping:
            return False
        agent = self._agent_name_mapping[agent_name]
        return (self.is_human_in_world(agent.world_name, human_id) and 
                human_id not in agent.excluded_humans)
        
    def register_dm(self, agent_name: str, dm_id: str) -> None:
        if agent_name in self._agent_name_mapping:
            self._agent_name_mapping[agent_name].dms.add(dm_id)
            
    def register_tool(self, agent_name: str, tool_id: str) -> None:
        if agent_name in self._agent_name_mapping:
            self._agent_name_mapping[agent_name].tools.add(tool_id)
            
    def get_agent_world(self, agent_name: str) -> Optional[str]:
        if agent_name in self._agent_name_mapping:
            return self._agent_name_mapping[agent_name].world_name
        return None
    
    def get_always_add_users(self) -> List[str]:
        return self._always_add_users
        
    def get_world_agents(self, world_name: str) -> Set[str]:
        return self._world_name_mapping.get(world_name, World()).agents
    
    def get_all_agent_names(self, world_name: str) -> list[str]:
        agents_in_world = self.get_world_agents(world_name)
        return [agent for agent in self._agent_name_mapping.keys() if agent in agents_in_world]
    
    def get_slack_app_id(self, agent_name: str, human_id: str) -> Optional[str]:
        """Get Slack user ID for a human if the agent can interact with them"""
        if agent_name in self._agent_name_mapping:
            if self.can_agent_interact_with_human(agent_name, human_id):
                agent = self._agent_name_mapping[agent_name]
                world = self._world_name_mapping.get(agent.world_name)
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
                    channel_members = agent.slack_client.get_channel_members(channel['id'])['members']
                    
                    # Only include DMs with members from the same world
                    channel_names = []
                    for member in channel_members:
                        member_name = self.name_from_any_id(member)
                        if member_name in self._agent_name_mapping:
                            if self._agent_name_mapping[member_name].world_name == agent.world_name:
                                channel_names.append(member_name)
                    
                    if channel_names:  # Only add if there are valid members from same world
                        all_channels.append(Channel(slack_id=channel['id'], name=",".join(channel_names)))
                        existing_channel_ids.add(channel['id'])
                    
        if channels.get('channels'):
            for channel in channels['channels']:
                # Only include channels from the agent's world
                if channel['id'] in self._channels_to_world and self._channels_to_world[channel['id']] == agent.world_name:
                    if channel['id'] not in existing_channel_ids:
                        all_channels.append(Channel(slack_id=channel['id'], name=channel['name']))
                        existing_channel_ids.add(channel['id'])
            
        # Update agent's channels with the combined list
        agent.channels = all_channels
