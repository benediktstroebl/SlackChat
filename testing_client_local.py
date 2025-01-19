from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="python", # Executable
    args=["server.py"], # Optional command line arguments
    env=None # Optional environment variables
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            
            # register world
            await session.register_world(name="test")

            # register agents
            await session.register_agent(name="test", world_name="test")
            await session.register_agent(name="test2", world_name="test")
            
            
            # List available tools
            tools = await session.list_tools()
            
            
            
            observation = await session.call_tool(name="echo_tool", arguments={"message": "Hello, world!"}, agent_name="test")
            
            observation = await session.call_tool(name="register_world", arguments={"message": "Hello, world!"}, agent_name="test")
            
            
            
            
            print(tools)
        

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())