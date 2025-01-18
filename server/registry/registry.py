from typing import Dict, Set, Optional
from dataclasses import dataclass, field

@dataclass
class AgentInfo:
    world_id: str
    slack_app_id: str
    channels: Set[str] = field(default_factory=set)
    dms: Set[str] = field(default_factory=set) 
    tools: Set[str] = field(default_factory=set)
    human_mappings: Dict[str, str] = field(default_factory=dict) # human_id -> slack_user_id

class Registry:
    def __init__(self):
        self._worlds: Dict[str, Set[str]] = {} # world_id -> set of agent_ids
        self._agents: Dict[str, AgentInfo] = {} # agent_id -> AgentInfo
        self._slack_apps: Dict[str, str] = {} # slack_app_id -> agent_id
        
    def register_world(self, world_id: str) -> None:
        if world_id not in self._worlds:
            self._worlds[world_id] = set()
            
    def register_agent(self, agent_id: str, world_id: str, slack_app_id: str) -> None:
        if world_id not in self._worlds:
            self.register_world(world_id)
            
        self._worlds[world_id].add(agent_id)
        self._agents[agent_id] = AgentInfo(world_id=world_id, slack_app_id=slack_app_id)
        self._slack_apps[slack_app_id] = agent_id
        
    def register_channel(self, agent_id: str, channel_id: str) -> None:
        if agent_id in self._agents:
            self._agents[agent_id].channels.add(channel_id)
            
    def register_dm(self, agent_id: str, dm_id: str) -> None:
        if agent_id in self._agents:
            self._agents[agent_id].dms.add(dm_id)
            
    def register_tool(self, agent_id: str, tool_id: str) -> None:
        if agent_id in self._agents:
            self._agents[agent_id].tools.add(tool_id)
            
    def register_human_mapping(self, agent_id: str, human_id: str, slack_user_id: str) -> None:
        if agent_id in self._agents:
            self._agents[agent_id].human_mappings[human_id] = slack_user_id
            
    def get_agent_world(self, agent_id: str) -> Optional[str]:
        if agent_id in self._agents:
            return self._agents[agent_id].world_id
        return None
        
    def get_world_agents(self, world_id: str) -> Set[str]:
        return self._worlds.get(world_id, set())
        
    def get_agent_by_slack_app(self, slack_app_id: str) -> Optional[str]:
        return self._slack_apps.get(slack_app_id)
        
    def get_agent_channels(self, agent_id: str) -> Set[str]:
        if agent_id in self._agents:
            return self._agents[agent_id].channels
        return set()
        
    def get_agent_dms(self, agent_id: str) -> Set[str]:
        if agent_id in self._agents:
            return self._agents[agent_id].dms
        return set()
        
    def get_agent_tools(self, agent_id: str) -> Set[str]:
        if agent_id in self._agents:
            return self._agents[agent_id].tools
        return set()
        
    def get_slack_user_id(self, agent_id: str, human_id: str) -> Optional[str]:
        if agent_id in self._agents:
            return self._agents[agent_id].human_mappings.get(human_id)
        return None
        
