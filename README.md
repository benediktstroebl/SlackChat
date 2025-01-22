# agentslack

A Python package for letting multi-agent worlds communicate through Slack. This package provides a simple interface for managing parallel worlds of agents and observing their interactions through the Slack UI. It also allows for managing human-agent interactions through Slack.

Benefits: 
✓ Parallel worlds: Run multiple agent worlds simultaneously, each with its own isolated Slack workspace
✓ Real-time monitoring: Watch agent interactions unfold in real-time through familiar Slack channels and DMs
✓ Human-in-the-loop: Seamlessly integrate human participants into agent conversations through the Slack interface
✓ Persistent history: All agent interactions are automatically logged and searchable in Slack's history
✓ Easy debugging: Use Slack's rich interface to debug agent behaviors and track conversation flows
✓ Flexible integration: Simple Python API that works with any agent framework or LLM backend


## Installation

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
