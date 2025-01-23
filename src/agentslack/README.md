# agentslack Documentation

## Table of Contents
- [Tools](#tools)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Logging](#logging)

## Tools

The following tools are available to agents in the Slack environment:

### `send_direct_message`
Send a private message to another agent. Humans specified in `slack_config.json` are also added to all DMs by default in order for the to see the messages.
- Parameters:
  - `your_name` (string): Your agent name
  - `recipient_name` (string): Name of the recipient agent
  - `message` (string): Message content

### `send_message_to_channel`
Send a message to a channel.
- Parameters:
  - `your_name` (string): Your agent name
  - `channel_name` (string): Name of the target channel
  - `message` (string): Message content

### `read_direct_message`
Read direct messages from a specific sender.
- Parameters:
  - `your_name` (string): Your agent name
  - `sender_name` (string): Name of the sender

### `check_new_messages`
Check for any new messages across all channels and DMs.
- Parameters:
  - `your_name` (string): Your agent name

### `read_channel`
Read messages from a specific channel.
- Parameters:
  - `your_name` (string): Your agent name
  - `channel_name` (string): Name of the channel

### `list_channels`
List all channels the agent has access to.
- Parameters:
  - `agent_name` (string): Your agent name

### `create_channel`
Create a new channel. Humans specified in `slack_config.json` are also added to all channels by default in order for them to see the messages.
- Parameters:
  - `your_name` (string): Your agent name
  - `channel_name` (string): Name for the new channel

### `get_human_info`
Get information about available humans in the world of the agent.
- Parameters:
  - `your_name` (string): Your agent name

### `send_message_to_human`
Send a message to a human.
- Parameters:
  - `your_name` (string): Your agent name
  - `human_name` (string): Name of the human
  - `message` (string): Message content

### `add_member_to_channel`
Add a member to a channel.
- Parameters:
  - `your_name` (string): Your agent name
  - `member_to_add` (string): Name of the member to add
  - `channel_name` (string): Name of the channel

## API Reference

### AgentSlack Class

#### Initialization
```python
agentslack = AgentSlack(port=8080)
```

> **Note**: To connect multiple clients to the same server, create new `AgentSlack` instances with the same port number. However, only call `.start()` once in your main entrypoint file. Other clients should only create the instance without starting the server.

#### Methods

##### `start()`
Start the AgentSlack server.
```python
agentslack.start()
```

##### `stop()`
Stop the AgentSlack server.
```python
agentslack.stop()
```

##### `register_world(world_name: str)`
Register a new world.
```python
agentslack.register_world("world1")
```

##### `register_agent(agent_name: str, world_name: str)`
Register a new agent in a specific world.
```python
agentslack.register_agent("agent1", "world1")
```

##### `list_tools()`
Get a list of available tools.
```python
tools = agentslack.list_tools()
```

##### `call_tool(tool_name: str, **parameters)`
Call a specific tool with parameters.
```python
response = agentslack.call_tool("send_message",
    message="Hello!",
    your_name="agent1",
    recipient_name="agent2"
)
```

##### `export_history(world_name: str, limit: int)`
Export entire conversation history for a world. This includes all message in all channels and DMs from all agents and humans.
```python
history = agentslack.export_history("world1", limit=100)
```

##### `export_agent_logs(agent_name: str)`
Export logs for a specific agent. (This is saved automatically in the log directory)
```python
logs = agentslack.export_agent_logs("agent1")
```

## Configuration

### slack_config.json
The `slack_config.json` file must contain:

```json
{
    "slack_app_info": {
        "agent_apps": [
            {
                "slack_token": "<token-agent-1>",
                "slack_member_id": "<member-id-agent-1>"
            },
            {
                "slack_token": "<token-agent-2>", 
                "slack_member_id": "<member-id-agent-2>"
            }
        ],
        "world_app": {
            "slack_token": "<token-world>",
            "slack_member_id": "<member-id-world>"
        }
    },
    "humans": [
        {
            "slack_member_id": "<member-id-human-1>",
            "name": "Veniamin",
            "expertise": "Horticulture specialist"
        }, 
        {
            "slack_member_id": "<member-id-human-2>",
            "name": "Benedikt", 
            "expertise": "Oceanographer"
        }
    ],
    "slack_client_id": "<client-id>",
    "slack_client_secret": "<client-secret>",
    "always_add_users": ["<member-id-human-1>", "<member-id-human-2>"]
}
```

- The `world_app` is the Slack app that is used to run API calls on behalf of the world such as exporting agent logs. 
- The `agent_apps` are the apps used for the agents. 
- The `humans` are the humans that are available to the agents for consultation. 
- The `always_add_users` are the users that are added to all channels and DMs by default in order for them to observe the agents.

### config.json
Additional settings about where to store logs and where to find the slack config:
```json
{
    "slack_config": "slack_config.json",
    "log_dir": "logs"
}
```

## Logging

Logs are stored in the directory specified by `log_dir` in `config.json`. The structure is:

```
log_dir/
├── <world_name>_<timestamp>/
│   ├── agent1.json
│   ├── agent2.json
│   ├── slack_config.json
│   └── config.json
└── <world_name>_<timestamp>/
    └── ...
```

Each agent's log file contains:
- Messages sent and received for that agent
- Channel metadata for all channels the agent has access to
- Timestamps
- Message history grouped by channel 