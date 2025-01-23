from typing import Optional

from smolagents import LiteLLMModel, tool
from smolagents.agents import ToolCallingAgent

from agentslack import AgentSlack


# Instantiate AgentSlack
agentslack = AgentSlack(port=8054)


@tool
def send_direct_message(message: str, your_name: str, recipient_name: str) -> str:
    """
    Send a direct message to another agents.
    Args:
        message: The message to send.
        your_name: The name of the agent sending the message.
        recipient_name: The name of the agent receiving the message.
    """
    return agentslack.call_tool("send_direct_message", message=message, your_name=your_name, recipient_name=recipient_name)

@tool
def list_channels(your_name: str) -> str:
    """
    List all channels you are in.
    Args:
        your_name: The name of the agent listing the channels.
    """
    return agentslack.call_tool("list_channels", your_name=your_name)

@tool
def send_message_to_channel(message: str, your_name: str, channel_name: str) -> str:
    """
    Send a message to a channel.
    Args:
        message: The message to send.
        your_name: The name of the agent sending the message.
        channel_name: The name of the channel to send the message to.
    """
    return agentslack.call_tool("send_message_to_channel", message=message, your_name=your_name, channel_name=channel_name)

@tool
def read_direct_message(your_name: str, sender_name: str) -> str:
    """
    Read a direct message from another agent.
    Args:
        your_name: The name of the agent reading the message.
        sender_name: The name of the agent sending the message.
    """
    return agentslack.call_tool("read_direct_message", your_name=your_name, sender_name=sender_name)

@tool
def read_channel(your_name: str, channel_name: str) -> str:
    """
    Read a message from a channel.
    Args:
        your_name: The name of the agent reading the message.
        channel_name: The name of the channel to read the message from.
    """
    return agentslack.call_tool("read_channel", your_name=your_name, channel_name=channel_name)

@tool
def create_channel(your_name: str, channel_name: str) -> str:
    """
    Create a new channel.
    Args:
        your_name: The name of the agent creating the channel.
        channel_name: The name of the channel to create.
    """
    return agentslack.call_tool("create_channel", your_name=your_name, channel_name=channel_name)


if __name__ == "__main__":
    import sys
    name = sys.argv[1] if len(sys.argv) > 1 else "a1"
    prompt = sys.argv[2] if len(sys.argv) > 2 else "You are agent a1. Communicate with other agents and use available tools."
    model = LiteLLMModel(model_id="gpt-4o-mini")
    a1 = ToolCallingAgent(
        tools=[send_direct_message, list_channels, send_message_to_channel, read_direct_message, read_channel], 
        model=model, 
        max_steps=10, 
        stream_json_logs=True, 
        json_logs_path=f"{name}.jsonl"
        )
    a1.run(prompt)


