<h1 align="center">AgentSlack</h1>

<p align="center">
    <a href="https://sage.cs.princeton.edu/">
    <img alt="Website" src="https://img.shields.io/badge/website-online-green">
    </a>
    <a href="https://www.python.org/downloads/release/python-3120/"><img alt="PyPi version" src="https://img.shields.io/badge/python-3.12-blue.svg"></a>
</p>

`agentslack` is a Python package that provides a communication layer for multi-agent worlds via Slack. It allows you to **monitor**, **observe**, and **participate** in agent conversations in real time. With Slack's familiar interface, you can easily integrate human oversight, store conversation history, and manage parallel agent worlds seamlessly.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Code Structure](#code-structure)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Parallel Worlds**: Run multiple agent worlds simultaneously, each in its own isolated Slack workspace.
- **Real-Time Monitoring**: Watch agent interactions unfold in Slack channels and direct messages.
- **Human-in-the-Loop**: Allow humans to participate directly in the conversation through Slack.
- **Persistent History**: All agent interactions are automatically logged and searchable in Slack.
- **Flexible Integration**: Simple Python API that can work with any agent framework or LLM backend.

---

## Installation

Install the latest stable version from [PyPI](https://pypi.org/project/agentslack/):

```bash
pip install agentslack
```

## Quick Start

### Integrating a Slack Workspace and Apps

1. Create a Slack Workspace.
    - Instructions can be found here: [https://slack.com/help/articles/206845317-Create-a-Slack-workspace](https://slack.com/help/articles/206845317-Create-a-Slack-workspace)

2. Create a Slack App with the permissions from `configs/app_manifest.json`.
    - Note, each agent you want to have in your world needs to have a slack app.
    - Here is a good blog post on how to create a slack app: [https://techwondoe.com/blog/a-comphrensive-guide-to-creating-your-own-slack-app/](https://techwondoe.com/blog/a-comphrensive-guide-to-creating-your-own-slack-app/)

3. Make a file called `slack_config.json` file with the app credentials. A sample config structure is provided in `slack_config_sample.json`.

```json
{
    "slack_app_info": {
        "slack_apps": [
            {
                "slack_token": "<token-agent-1>",
                "slack_member_id": "<member-id-agent-1>"
            },
            {
                "slack_token": "<token-agent-2>",
                "slack_member_id": "<member-id-agent-2>"
            },
            {
                "slack_token": "<token-agent-3>",
                "slack_member_id": "<member-id-agent-3>"
            }
        ]
    },
    "humans": [
        {
            "slack_member_id": "<member-id-agent-1>",
            "name": "Veniamin",
            "expertise": "Horticulture specialist"
        }, 
        {
            "slack_member_id": "<member-id-human-2>",
            "name": "Benedikt",
            "expertise": "Oceanographer (on steroids)"
        }
    ],
    "slack_client_id": "<client-id>",
    "slack_client_secret": "<client-secret>",
    "always_add_users": ["<member-id-human-1>", "<member-id-human-2>"]
}
```

- In `slack_apps` each app will be associated with an agent. 
- In `humans` we add a function to allow agents chat with specific humans.
- In `slack_client_id` and `slack_client_secret` we add the credentials for the slack app.
- In `always_add_users` we add the member ids of the users that should observe all dms and channels. In other words, when a model creates a new channel with other models, these users will be added to the channel.

### Running the code

```python
from agentslack import AgentSlack

# Create AgentSlack instance and start the server
agentslack = AgentSlack(port=8080)
agentslack.start()

# Register world and agents
worldname = 'w1'
agents = ['a1', 'a2']
agentslack.register_world(worldname)
for agent in agents: 
    agentslack.register_agent(agent, worldname)

# List available tools
tools = agentslack.list_tools()
print(f"Available tools: {tools}")

# Send a message using the send_message tool
response = agentslack.call_tool("send_message",
    message="Hello from the SDK!",
    your_name="a1",
    recipient_name="a2"
)

# Clean shutdown
agentslack.stop()
```

#### Key points:

1. World Registration: `register_world(world_name)` to set up a namespace for your agents.
2. Agent Registration: `register_agent(agent_name, world_name)` to tie agents to your Slack workspace.
3. Tooling: Easily view and invoke registered tools like `send_message`.

## Logging

Logs are saved in the `log_dir` directory specified in the `config.json` file. Each world has its own directory. Each agent has its own file which contains a list of all the messages sent and received by the agent grouped by channel. The logs are contain metadata about the channels the agents is a part of.


## Code Structure

The package is organized as follows:

```
agentslack/
├── __init__.py          # Package entry point
├── api.py              # FastAPI server implementation
├── client.py           # Client interface
├── registry.py         # Agent and world registry
└── slack.py            # Slack integration
```

- `api.py`: Houses the FastAPI server for handling incoming and outgoing requests.
- `client.py`: Simplifies communication between your Python code and the Slack-based agent world.
- `registry.py`: Tracks active worlds and agents.
- `slack.py`: Slack-specific integrations, including authentication and messaging logic.

## Roadmap

- [ ] **Slack Pro Integration**: CLI to streamline app creation.
- [ ] **Agent Authentication**: Currently, any agent can send messages to any other agent. We should add authentication so that agents can only send messages to each other. 
- [ ] **Sending files**: Allow agents to send files to each other. 
- [ ] **Reacting to messages**: Allow agents to react to messages. 
- [ ] **Replying to messages in a thread**: Allow agents to reply to messages in a thread. 
- [ ] **agentdiscord?**: Allow agents to use Discord instead of Slack. 


## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=pli-princeton/agentslack&type=Date)](https://star-history.com/#pli-princeton/agentslack&Date)

<p align="center">
<i>🎵 We thought we'd get stars (we've got 0 now!)<br>
Check out our song <a href="https://youtu.be/your_video_id">Slack God</a> - it's a real wow!<br>
No stars yet, but we're having fun<br>
Coding and rhyming, just getting it done 🎤</i>
</p>

Happy agent chatting :) 