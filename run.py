from agentslack import AgentSlack
import os


# Create client (which also starts the server)
agentslack = AgentSlack(port=8080)
agentslack.start()

# we require each agent to have a name attribute 
worldname = 'w1'
agents = ['a1', 'a2', 'a3']

agentslack.register_world(worldname)
for agent in agents: 
    agentslack.register_agent(agent, worldname)
    # each agent gets a slack app id 

# List available tools
tools = agentslack.list_tools()
print(f"Available tools: {tools}")

humans = agentslack.call_tool("get_human_info")

# send dm to a2
send_direct_message = agentslack.call_tool("send_direct_message",
    your_name="a1",
    recipient_name="a2",
    message="Slack GOD"
)

send_direct_message = agentslack.call_tool("send_direct_message",
    your_name="a1",
    recipient_name="a2",
    message="Slack GOD"
)

send_direct_message = agentslack.call_tool("send_direct_message",
    your_name="a3",
    recipient_name="a2",
    message="Slack GOD"
)

send_message_to_human = agentslack.call_tool("send_human_message",
    your_name="a1",
    human_name="Benedikt",
    message="Hey big B, heard you're a big fan of Slack. What's your favorite Slack feature?"
)



add_member_to_channel = agentslack.call_tool("add_member_to_channel",
    your_name="a1",
    member_to_add="a2",
    channel_name="test3"
)

print(f"Humans: {humans}")
exit()

# # Example: Send a message using call_tool
# response = agentslack.call_tool("send_direct_message",
#     message="Hello from the SDK!",
#     your_name="a1",
#     recipient_name="a2"
# )
# response = agentslack.call_tool("send_message_to_channel",
#     message="""Look, I was gonna go easy on you not to flood your mentions
# But I'm only going to get this one chance
# (new message-, new message-)
# Something's wrong, I can feel it
# (new message, Slack channel, you're on!)
# Just a feeling I've got, like something's about to happen, but I don't know what
# If that means what I think it means, we're in trouble, big trouble
# And if IT is as buggy as they say, I'm not taking any chances
# You are just what the team ordered

# [Chorus]
# I'm beginnin' to feel like a Slack God, Slack God
# All my people from the huddle to the chat log, chat log
# Now, who thinks their threads are long enough to backlog, backlog?
# They said I Slack like a pro bot, so call me Slack-bot

# [Verse 1]
# But for me to chat like an expert, it must be in my teams
# I got a shortcut in my dock socket
# My fingers fly off when I hotkey it
# Got a fat stack from those app profits
# Made a livin' and a killin' off it
# Ever since the office turned remote and chaotic
# With Zoom calls feelin' kinda robotic
# I'm an admin still as flawless
# But as swamped and as confused as all hell
# Channels, skill-a-holic (fill 'em all with)

# [Verse 2]
# This clickity typity-hippity thread hop
# You don't really wanna get into a pingin' match
# With this chattity brat, stackin' up tasks in the back of the app
# Back-to-back Slack attack, yap-yap, talkin' in caps
# And at the exact same time, I attempt these channel management stunts while I'm practicin' that
# I'll still be able to break a mother-lovin' inbox
# Over the back of a couple of unread DMs and crack it in half

# [Bridge]
# Only realized it was ironic, I was signed into Slack after the fact
# How could I not blow? All I do is drop pings
# Feel my wrath of @everyone
# Teams are havin' a rough time period, here's a status pad
# It's actually disastrously bad for the lag
# While I'm masterfully structuring this workspace

# [Chorus]
# 'Cause I'm beginnin' to feel like a Slack God, Slack God
# All my people from the huddle to the chat log, chat log
# Now, who thinks their threads are long enough to backlog, backlog?
# Let me show you maintainin' this flow ain't that hard, that hard
# Everybody want the key and the secret to Slack immortality like I have got""",
#     channel_name="test3",
#     your_name="a1"
# )


channels = agentslack.call_tool("send_direct_message",
    your_name="a1",
    recipient_name="a2",
    message="Slack GOD"
)



channels = agentslack.call_tool("send_message_to_channel",
    your_name="a1",
    message="Slack GO2D",
    channel_name="test3"
)


channels = agentslack.call_tool("list_channels",
    your_name="a1"
)
print(f"Channels: {channels}")


channel_name = channels[0]['name']
print(f"Channel name: {channel_name}")
messages = agentslack.call_tool("check_new_messages",
    your_name="a2"
)
print(f"Messages: {messages}")

# Clean shutdown
agentslack.stop()

