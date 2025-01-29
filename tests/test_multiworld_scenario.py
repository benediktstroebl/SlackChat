import time
from agentslack import AgentSlack

# Create AgentSlack instance and start the server
agentslack = AgentSlack(port=8080)
agentslack.start()

print("\n=== Testing Multi-World Isolation ===\n")

# Register first world and agents
print("[WORLD 1 SETUP]")
world1 = 'AgentZoo'
agents_world1 = ['Alice', 'Bob']
agentslack.register_world(world1)
for agent in agents_world1: 
    agentslack.register_agent(agent, world1)
print(f"Created world '{world1}' with agents: {agents_world1}")

# Register second world and agents
print("\n[WORLD 2 SETUP]")
world2 = 'AgentZoo_2'
agents_world2 = ['Charlie']
agentslack.register_world(world2)
for agent in agents_world2: 
    agentslack.register_agent(agent, world2)
print(f"Created world '{world2}' with agents: {agents_world2}")

# Test 1: Intra-world communication (should work)
print("\n[TEST 1: INTRA-WORLD COMMUNICATION]")
print("Sending message from Bob to Alice (same world):")
response = agentslack.call_tool("send_direct_message",
    message="Hello Alice, let's create a zoology channel!",
    your_name="Bob",
    recipient_name="Alice"
)
print(f"Response: {response}")

# Test 2: Inter-world communication (should fail)
print("\n[TEST 2: INTER-WORLD COMMUNICATION]")
print("Attempting to send message from Charlie to Alice (different worlds):")
response = agentslack.call_tool("send_direct_message",
    message="Hello Alice from another world!",
    your_name="Charlie",
    recipient_name="Alice"
)
print(f"Response: {response}")

# Test 3: Channel creation and isolation
print("\n[TEST 3: CHANNEL CREATION AND ISOLATION]")
print("Creating channels in both worlds:")

# Create channel in World 1
response = agentslack.call_tool("create_channel",
    channel_name="world1-zoology",
    your_name="Alice"
)
print(f"World 1 channel creation: {response}")

# Create channel in World 2
response = agentslack.call_tool("create_channel",
    channel_name="world2-zoology",
    your_name="Charlie"
)
print(f"World 2 channel creation: {response}")

# Test 4: Channel visibility
print("\n[TEST 4: CHANNEL VISIBILITY]")
print("Checking channel visibility for agents in different worlds:")

# List channels for World 1 agent
response = agentslack.call_tool("list_channels",
    your_name="Bob"
)
print(f"Bob's visible channels (World 1): {response}")

# List channels for World 2 agent
response = agentslack.call_tool("list_channels",
    your_name="Charlie"
)
print(f"Charlie's visible channels (World 2): {response}")

# Test 5: Cross-world channel access
print("\n[TEST 5: CROSS-WORLD CHANNEL ACCESS]")
print("Attempting to read channel from another world:")
response = agentslack.call_tool("read_channel",
    channel_name="world1-zoology",
    your_name="Charlie"
)
print(f"Charlie attempting to read World 1 channel: {response}")

# Test 6: Cross-world member addition
print("\n[TEST 6: CROSS-WORLD MEMBER ADDITION]")
print("Attempting to add member from another world to channel:")
response = agentslack.call_tool("add_member_to_channel",
    channel_name="world1-zoology",
    your_name="Alice",
    member_to_add="Charlie"
)
print(f"Response: {response}")

# Test 7: Message broadcasting in isolated channels
print("\n[TEST 7: MESSAGE BROADCASTING]")
# Send message in World 1 channel
response = agentslack.call_tool("send_message_to_channel",
    message="Hello World 1!",
    your_name="Bob",
    channel_name="world1-zoology"
)
print(f"Bob sending message in World 1 channel: {response}")

# Try to send message to World 1 channel from World 2 agent
response = agentslack.call_tool("send_message_to_channel",
    message="Hello from World 2!",
    your_name="Charlie",
    channel_name="world1-zoology"
)
print(f"Charlie attempting to send message to World 1 channel: {response}")

# Test 8: Check new messages isolation
print("\n[TEST 8: NEW MESSAGES ISOLATION]")
print("Checking new messages for agents in different worlds:")
response = agentslack.call_tool("check_new_messages",
    your_name="Charlie"
)
print(f"Charlie's new messages (World 2): {response}")

response = agentslack.call_tool("check_new_messages",
    your_name="Alice"
)
print(f"Alice's new messages (World 1): {response}")

print("\n=== Multi-World Isolation Testing Complete ===\n")

# Clean shutdown
agentslack.stop()