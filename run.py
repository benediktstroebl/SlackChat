from agentslack import AgentSlack
import os

# Configure Slack settings
slack_config = {
    "slack_bot_token": os.getenv("SLACK_BOT_TOKEN"),
    "slack_client_id": os.getenv("SLACK_CLIENT_ID"),
    "slack_client_secret": os.getenv("SLACK_CLIENT_SECRET"),
    "slack_channel_id": os.getenv("SLACK_CHANNEL_ID")
}

# Create client (which also starts the server)
agentslack = AgentSlack(port=8080, slack_config=slack_config)

# List available tools
tools = agentslack.list_tools()
print(f"Available tools: {tools}")

# Example: Send a message using call_tool
response = agentslack.call_tool("send_message",
    message="Hello from the SDK!",
    target_channel_id=os.getenv("SLACK_CHANNEL_ID")
)
print(f"Message sent: {response}")

# Clean shutdown
agentslack.stop()

