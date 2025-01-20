from dataclasses import dataclass, field
from typing import Set, Dict
from agentslack.Slack import Slack

@dataclass 
class Message:
    message: str
    channel_id: str
    user_id: str
    timestamp: str

@dataclass
class SlackApp:
    slack_id: str
    slack_token: str 

@dataclass 
class Channel:
    slack_id: str
    name: str 


@dataclass
class Agent:
    world_name: str
    agent_name: str 
    slack_app: SlackApp
    channels: list[Channel] = field(default_factory=list)
    read_messages: dict[str, list[str]] = field(default_factory=dict)
    slack_client: Slack = None 
    dms: Set[str] = field(default_factory=set)
    tools: Set[str] = field(default_factory=set)
    included_humans: Set[str] = field(default_factory=set) # humans this agent can't interact with

@dataclass
class World:
    agents: Set[str] = field(default_factory=set)
    humans: Set[str] = field(default_factory=set)
    slack_client: Slack = None 
    channels: list[Channel] = field(default_factory=list)
    human_mappings: Dict[str, str] = field(default_factory=dict) # human_id -> slack_app_id
