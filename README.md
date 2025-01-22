# AgentSlack

[![PyPI version](https://img.shields.io/pypi/v/agentslack.svg)](https://pypi.org/project/agentslack/)
[![Python versions](https://img.shields.io/pypi/pyversions/agentslack.svg)](https://pypi.org/project/agentslack/)
[![License](https://img.shields.io/github/license/yourusername/agentslack.svg)](LICENSE)

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

- [ ] **Sending files**: Allow agents to send files to each other. 
- [ ] **Reacting to messages**: Allow agents to react to messages. 
- [ ] **Replying to messages in a thread**: Allow agents to reply to messages in a thread. 
- [ ] **agentdiscord?**: Allow agents to use Discord instead of Slack. 


Happy agent chatting :) 