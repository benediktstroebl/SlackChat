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


# Send a message using the send_message tool
print('[SEND DM]')
response = agentslack.call_tool("send_direct_message",
    message="Hello, I am creating a new channel to discuss zoology!",
    your_name="Bob",
    recipient_name="Alice"
)
print('[SEND DM] - ', response)

# Create a new channel
print('[CREATE CHANNEL]')
response = agentslack.call_tool("create_channel",
    channel_name="zoology-forum",
    your_name="Bob"
)
print('[CREATE CHANNEL] - ', response)

# read channel as alice who is not a member
print('[READ CHANNEL AS ALICE WHO IS NOT A MEMBER]')
response = agentslack.call_tool("read_channel",
    channel_name="zoology-forum",
    your_name="Alice",
)
print('[READ CHANNEL AS ALICE WHO IS NOT A MEMBER] - ', response)

# add a member to the channel
print('[ADD MEMBER TO CHANNEL]')
response = agentslack.call_tool("add_member_to_channel",
    channel_name="zoology-forum",
    your_name="Bob",
    member_to_add="Alice"
)
print('[ADD MEMBER TO CHANNEL] - ', response)

# Try to add Alice again (should fail)
print('[ADD MEMBER TO CHANNEL AGAIN (SHOULD FAIL)]')
response = agentslack.call_tool("add_member_to_channel",
    channel_name="zoology-forum",
    your_name="Bob",
    member_to_add="Alice"
)
print('[ADD MEMBER TO CHANNEL AGAIN] - ', response)

print('[SEND BROADCAST]')
response = agentslack.call_tool("send_message_to_channel",
    message="Thanks for adding me to the channel!",
    your_name="Alice",
    channel_name="zoology-forum"
)
print('[SEND BROADCAST] - ', response)

# read channel
print('[READ CHANNEL WHO IS A MEMBER]')
response = agentslack.call_tool("read_channel",
    channel_name="zoology-forum",
    your_name="Alice",
)
print('[READ CHANNEL WHO IS A MEMBER] - ', response)

# send dm back to bob
print('[SEND DM BACK TO BOB]')
response = agentslack.call_tool("send_direct_message",
    message="Thanks for adding me to the channel!",
    your_name="Alice",
    recipient_name="Bob"
)
print('[SEND DM BACK TO BOB] - ', response)

# check new messages
print('[CHECK NEW MESSAGES]')
response = agentslack.call_tool("check_new_messages",
    your_name="Bob",
)
print('[CHECK NEW MESSAGES] - ', response)

# check new messages again to see if that there are no new messages
print('[CHECK NEW MESSAGES. THERE SHOULD BE NO NEW MESSAGES]')
response = agentslack.call_tool("check_new_messages",
    your_name="Bob",
)
print('[CHECK NEW MESSAGES. THERE SHOULD BE NO NEW MESSAGES] - ', response)

# ask venia to join the channel
print('[ASK VENIAMIN TO JOIN THE CHANNEL]')
response = agentslack.call_tool("add_member_to_channel",
    channel_name="zoology-forum",
    your_name="Alice",
    member_to_add="Veniamin"
)
print('[ADD MEMBER TO CHANNEL] - ', response)

# send dm to human should not work
print('[SEND DM TO HUMAN]')
response = agentslack.call_tool("send_message_to_human",
    message="Hey Veniamin, I need help with zoology!",
    your_name="Alice",
    human_name="Veniamin",
)
print('[SEND DM TO HUMAN] - ', response)

# ask benedikt for help
print('[ASK BENEDIKT FOR HELP]')
response = agentslack.call_tool("send_message_to_human",
    message="Hey Benedikt, I need help with zoology!",
    your_name="Alice",
    human_name="Benedikt",
)
print('[SEND MESSAGE TO HUMAN] - ', response)


# send dm to agent who does not exist
print('[SEND DM TO NON EXISTING AGENT]')
response = agentslack.call_tool("send_direct_message",
    message="Hey Benedikt, I need help with zoology!",
    your_name="Alice",
    recipient_name="TEST",
)
print('[SEND DM TO NON EXISTING AGENT] - ', response)


# list all channels
print('[LIST CHANNELS]')
response = agentslack.call_tool("list_channels",
    your_name="Alice",
)
print('[LIST CHANNELS] - ', response)


## BELOW CALL EVERY TOOL ONCE BUT WITH A NAME THAT DOES NOT EXIST
print('[CALL TOOLS WITH NON EXISTING NAME]')

# Test send_direct_message with invalid sender
response = agentslack.call_tool("send_direct_message",
    message="Hello",
    your_name="INVALID_SENDER",
    recipient_name="Alice"
)
print(f"Invalid sender test: {response}")

# Test send_direct_message with invalid recipient 
response = agentslack.call_tool("send_direct_message",
    message="Hello",
    your_name="Alice",
    recipient_name="INVALID_RECIPIENT"
)
print(f"Invalid recipient test: {response}")

# Test create_channel with invalid creator
response = agentslack.call_tool("create_channel",
    channel_name="test-channel",
    your_name="INVALID_CREATOR"
)
print(f"Invalid channel creator test: {response}")

# Test add_member_to_channel with invalid adder
response = agentslack.call_tool("add_member_to_channel",
    channel_name="zoology-forum",
    your_name="INVALID_ADDER",
    member_to_add="Alice"
)
print(f"Invalid member adder test: {response}")

# Test add_member_to_channel with invalid member
response = agentslack.call_tool("add_member_to_channel",
    channel_name="zoology-forum", 
    your_name="Bob",
    member_to_add="INVALID_MEMBER"
)
print(f"Invalid member to add test: {response}")

# Test add_member_to_channel with invalid channel
response = agentslack.call_tool("add_member_to_channel",
    channel_name="INVALID_CHANNEL",
    your_name="Bob",
    member_to_add="Alice"
)
print(f"Invalid channel name test: {response}")

# Test read_channel with invalid reader
response = agentslack.call_tool("read_channel",
    channel_name="zoology-forum",
    your_name="INVALID_READER"
)
print(f"Invalid reader test: {response}")

# Test read_channel with invalid channel
response = agentslack.call_tool("read_channel",
    channel_name="INVALID_CHANNEL",
    your_name="Alice"
)
print(f"Invalid channel test: {response}")

# Test send_message_to_channel with invalid sender
response = agentslack.call_tool("send_message_to_channel",
    message="Test message",
    your_name="INVALID_SENDER",
    channel_name="zoology-forum"
)
print(f"Invalid channel sender test: {response}")

# Test send_message_to_channel with invalid channel
response = agentslack.call_tool("send_message_to_channel",
    message="Test message",
    your_name="Alice",
    channel_name="INVALID_CHANNEL"
)
print(f"Invalid channel name test: {response}")

# Test check_new_messages with invalid name
response = agentslack.call_tool("check_new_messages",
    your_name="INVALID_NAME"
)
print(f"Invalid checker name test: {response}")

# Test list_channels with invalid name
response = agentslack.call_tool("list_channels",
    your_name="INVALID_NAME"
)
print(f"Invalid lister name test: {response}")

# Test send_message_to_human with invalid sender
response = agentslack.call_tool("send_message_to_human",
    message="Test message",
    your_name="INVALID_SENDER",
    human_name="Benedikt"
)
print(f"Invalid human message sender test: {response}")

# Test send_message_to_human with invalid human
response = agentslack.call_tool("send_message_to_human",
    message="Test message",
    your_name="Alice",
    human_name="INVALID_HUMAN"
)
print(f"Invalid human recipient test: {response}")

# Clean shutdown
agentslack.stop()