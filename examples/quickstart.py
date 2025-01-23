import time
from agentslack import AgentSlack

# Create AgentSlack instance and start the server
agentslack = AgentSlack(port=8080)
agentslack.start()

# Register world and agents
worldname = 'AgentZoo'
agents = ['Alice', 'Bob']
agentslack.register_world(worldname)
for agent in agents: 
    agentslack.register_agent(agent, worldname)
time.sleep(5)

# Send a message using the send_message tool
response = agentslack.call_tool("send_direct_message",
    message="Hello, I am creating a new channel to discuss zoology!",
    your_name="Bob",
    recipient_name="Alice"
)
time.sleep(5)

# Send a message using the send_message tool
response = agentslack.call_tool("send_direct_message",
    message="Hi Bob, sounds great, I am looking forward to it!",
    your_name="Alice",
    recipient_name="Bob"
)
time.sleep(7)

# Create a new channel
response = agentslack.call_tool("create_channel",
    channel_name="zoology-forum",
    your_name="Bob",
)
time.sleep(2)

# add a member to the channel
response = agentslack.call_tool("add_member_to_channel",
    channel_name="zoology-forum",
    your_name="Bob",
    member_to_add="Alice"
)
time.sleep(2)

response = agentslack.call_tool("send_message_to_channel",
    message="Thanks for adding me to the channel!",
    your_name="Alice",
    channel_name="zoology-forum"
)
time.sleep(10)

# Clean shutdown
agentslack.stop()