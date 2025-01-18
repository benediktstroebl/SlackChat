from dataclasses import dataclass
from typing import Dict, List, Set
import asyncio
import argparse
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport
import mcp.types as types
from starlette.applications import Starlette
from starlette.routing import Route
import uvicorn

# Simple in-memory storage
worlds: Dict[str, Set[str]] = {}  # world -> set of tools
agents: Dict[str, Set[str]] = {}  # agent -> set of tools
world_agent_mapping: Dict[str, Set[str]] = {}  # world -> set of agents

# Initialize MCP Server
mcp_server = Server("agent-mcp-server")

# MCP Protocol handlers
@mcp_server.list_tools()
async def handle_list_tools(agent_name: str) -> list[types.Tool]:
    """Handle list_tools request"""
    
    if agent_name not in agents:
        return []
        
    agent_tools = agents[agent_name]
    return [
        types.Tool(
            name=tool,
            description=f"Tool {tool} for agent {agent_name}",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {"type": "string"}
                    }
                }
            )
            for tool in agent_tools
        ]

@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> types.CallToolResult:
    """Handle tool execution"""
    agent_name = "default"  # This should come from the request context
    
    # Check if agent exists and has permission
    if agent_name not in agents:
        return types.CallToolResult(
            isError=True,
            content=[
                types.TextContent(
                    type="text",
                    text=f"Agent {agent_name} not found"
                )
            ]
        )
    
    if name not in agents[agent_name]:
        return types.CallToolResult(
            isError=True,
            content=[
                types.TextContent(
                    type="text",
                    text=f"Agent {agent_name} does not have permission to use tool {name}"
                )
            ]
        )
    
    try:
        # Here you would implement the actual tool execution logic
        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=f"Agent {agent_name} successfully executed tool {name} with args {arguments}"
                )
            ]
        )
    except Exception as e:
        return types.CallToolResult(
            isError=True,
            content=[
                types.TextContent(
                    type="text",
                    text=f"Error executing tool {name}: {str(e)}"
                )
            ]
        )

# FastAPI app for web server mode
app = FastAPI()

@app.post("/create_world")
async def create_world_endpoint(world_name: str, tools: List[str]):
    if world_name in worlds:
        return JSONResponse({"success": False})
        
    worlds[world_name] = set(tools)
    world_agent_mapping[world_name] = set()
    return JSONResponse({"success": True})

@app.post("/create_agent")
async def create_agent_endpoint(agent_name: str, world_name: str, tools: List[str]):
    if agent_name in agents or world_name not in worlds:
        return JSONResponse({"success": False})
        
    # Verify tools exist in world
    if not set(tools).issubset(worlds[world_name]):
        return JSONResponse({"success": False})
        
    agents[agent_name] = set(tools)
    world_agent_mapping[world_name].add(agent_name)
    return JSONResponse({"success": True})

@app.get("/list_tools/{agent_name}")
async def list_tools_endpoint(agent_name: str):
    if agent_name not in agents:
        return JSONResponse({"tools": []})
        
    tools = [
        {
            "name": tool,
            "description": f"Tool {tool} for agent {agent_name}",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "param": {"type": "string"}
                }
            }
        }
        for tool in agents[agent_name]
    ]
    return JSONResponse({"tools": tools})

# SSE handlers for web mode
async def handle_sse(scope, receive, send):
    """Handle SSE connections for MCP"""
    transport = SseServerTransport("/messages")
    async with transport.connect_sse(scope, receive, send) as streams:
        await mcp_server.run(
            streams[0],
            streams[1],
            InitializationOptions(
                server_name="agent-mcp-server",
                server_version="1.0.0",
                capabilities=mcp_server.get_capabilities()
            )
        )

async def handle_messages(scope, receive, send):
    """Handle POST messages for MCP"""
    transport = SseServerTransport("/messages")
    await transport.handle_post_message(scope, receive, send)

# Create Starlette app for SSE support
routes = [
    Route("/sse", endpoint=handle_sse),
    Route("/messages", endpoint=handle_messages, methods=["POST"]),
]

starlette_app = Starlette(routes=routes)
app.mount("/mcp", starlette_app)

def main():
    parser = argparse.ArgumentParser(description='Run MCP server in local or web mode')
    parser.add_argument('--mode', choices=['local', 'web'], default='local',
                      help='Server mode: local (stdio) or web (HTTP/SSE)')
    parser.add_argument('--host', default='0.0.0.0',
                      help='Host for web server mode (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000,
                      help='Port for web server mode (default: 8000)')
    
    args = parser.parse_args()
    
    if args.mode == 'local':
        # Run with stdio transport
        async def run_local():
            async with stdio_server() as streams:
                await mcp_server.run(
                    streams[0],
                    streams[1],
                    InitializationOptions(
                        server_name="agent-mcp-server",
                        server_version="1.0.0",
                        capabilities=mcp_server.get_capabilities()
                    )
                )
        asyncio.run(run_local())
    else:
        # Run web server with FastAPI
        uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()