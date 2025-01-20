from agentslack import AgentSlack
import asyncio
import subprocess

agentslack = AgentSlack(port=8080)

# Register world and agents
worldname = 'w1'
agents = ['a1', 'a2']
agentslack.register_world(worldname)
for agent in agents: 
    agentslack.register_agent(agent, worldname)
    
    
# run agent.py three times concurrently
async def run_agent(agent_name):
    prompts = {
        'a1': "You are agent a1. Ask a2 a question in a channel.",
        'a2': "You are agent a2. Respond to the last message in the channel. Say someting concrete to the a1 that makes it clear you are responding to the message.",
        'a3': "You are agent a3. Respond to all message from a2."
    }
    
    process = await asyncio.create_subprocess_exec('python', 'agent.py', agent_name, prompts[agent_name])
    await process.communicate()

async def main():
    tasks = [run_agent(agent) for agent in agents]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
