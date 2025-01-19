from typing import Dict, Set, Optional
from dataclasses import dataclass, field

class RegistryError(Exception):
    """Base exception for registry errors"""
    pass

class DuplicateAgentError(RegistryError):
    """Raised when trying to register an agent with a name that already exists"""
    pass

class DuplicateWorldError(RegistryError):
    """Raised when trying to register a world with a name that already exists"""
    pass

@dataclass
class Agent:
    world_name: str
    slack_app_id: str
    channels: Set[str] = field(default_factory=set)
    dms: Set[str] = field(default_factory=set)
    tools: Set[str] = field(default_factory=set)
    excluded_humans: Set[str] = field(default_factory=set) # humans this agent can't interact with

@dataclass
class World:
    agents: Set[str] = field(default_factory=set)
    humans: Set[str] = field(default_factory=set)
    human_mappings: Dict[str, str] = field(default_factory=dict) # human_id -> slack_user_id

class Registry:
    def __init__(self):
        self._worlds: Dict[str, World] = {} # world_name -> World
        self._agents: Dict[str, Agent] = {} # agent_name -> Agent
        self._slack_apps: Dict[str, str] = {} # slack_app_id -> agent_name
        
    def register_world(self, world_name: str) -> None:
        """Register a new world. Raises DuplicateWorldError if name already exists."""
        if world_name in self._worlds:
            raise DuplicateWorldError(f"World '{world_name}' already exists")
        self._worlds[world_name] = World()
            
    def register_agent(self, agent_name: str, world_name: str, slack_app_id: str) -> None:
        """Register a new agent. Raises DuplicateAgentError if name already exists."""
        if agent_name in self._agents:
            raise DuplicateAgentError(f"Agent '{agent_name}' already exists")
            
        # Create world if it doesn't exist
        if world_name not in self._worlds:
            self.register_world(world_name)
            
        self._worlds[world_name].agents.add(agent_name)
        self._agents[agent_name] = Agent(world_name=world_name, slack_app_id=slack_app_id)
        self._slack_apps[slack_app_id] = agent_name

    def world_exists(self, world_name: str) -> bool:
        """Check if a world exists"""
        return world_name in self._worlds

    def agent_exists(self, agent_name: str) -> bool:
        """Check if an agent exists"""
        return agent_name in self._agents

    def register_human_in_world(self, world_name: str, human_id: str, slack_user_id: str) -> None:
        """Register a human in a world with their Slack user ID mapping"""
        if world_name not in self._worlds:
            self.register_world(world_name)
        world = self._worlds[world_name]
        world.humans.add(human_id)
        world.human_mappings[human_id] = slack_user_id

    def remove_human_from_world(self, world_name: str, human_id: str) -> None:
        if world_name in self._worlds:
            world = self._worlds[world_name]
            world.humans.discard(human_id)
            world.human_mappings.pop(human_id, None)
            
    def get_world_humans(self, world_name: str) -> Set[str]:
        return self._worlds.get(world_name, World()).humans

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
        
    def register_channel(self, agent_name: str, channel_id: str) -> None:
        if agent_name in self._agents:
            self._agents[agent_name].channels.add(channel_id)
            
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
        
    def get_world_agents(self, world_name: str) -> Set[str]:
        return self._worlds.get(world_name, World()).agents
    
    def get_all_agents(self) -> Set[str]:
        return set(self._agents.keys())
        
    def get_agent_by_slack_app(self, slack_app_id: str) -> Optional[str]:
        return self._slack_apps.get(slack_app_id)
        
    def get_agent_channels(self, agent_name: str) -> Set[str]:
        if agent_name in self._agents:
            return self._agents[agent_name].channels
        return set()
        
    def get_agent_dms(self, agent_name: str) -> Set[str]:
        if agent_name in self._agents:
            return self._agents[agent_name].dms
        return set()
        
    def get_agent_tools(self, agent_name: str) -> Set[str]:
        if agent_name in self._agents:
            return self._agents[agent_name].tools
        return set()
        
    def get_slack_user_id(self, agent_name: str, human_id: str) -> Optional[str]:
        """Get Slack user ID for a human if the agent can interact with them"""
        if agent_name in self._agents:
            if self.can_agent_interact_with_human(agent_name, human_id):
                agent = self._agents[agent_name]
                world = self._worlds.get(agent.world_name)
                if world:
                    return world.human_mappings.get(human_id)
        return None
        
