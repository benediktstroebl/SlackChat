from agentslack import AgentSlack
import asyncio
import subprocess

agentslack = AgentSlack(port=8054)
agentslack.start()

# Register world and agents
worldname = 'w1'
agents = ['a1', 'a2']
agentslack.register_world(worldname)
for agent in agents: 
    agentslack.register_agent(agent, worldname)
    
    
# run agent.py three times concurrently
async def run_agent(agent_name):
    prompts = {
        'a1': "You are agent a1. Collaborate with the other agents.",
        'a2': "You are agent a2. Collaborate with the other agents.",
        'a3': "You are agent a3. Collaborate with the other agents."
    }
    
    process = await asyncio.create_subprocess_exec('python', 'agent.py', agent_name, prompts[agent_name])
    await process.communicate()

async def main():
    tasks = [run_agent(agent) for agent in agents]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())