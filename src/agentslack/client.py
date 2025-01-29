import requests
from typing import Dict, Any, List, Optional
from .api import Tool, Server

class Client:
    def __init__(self, 
                 host: str = "localhost", 
                 port: int = 8000):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.server = None


    def start(self):
        """Start a new server instance"""
        self.server = Server(host=self.host, port=self.port)
        self.server.start()

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        response = requests.get(f"{self.base_url}/tools")
        return response.json()
        
    def call_tool(self, tool_name: str, **parameters: Any) -> Dict[str, Any]:
        """Call a specific tool with parameters"""
        response = requests.post(
            f"{self.base_url}/tools/{tool_name}",
            json=parameters
        )
    
        return response.json()

    def register_world(self, world_name: str) -> None: 
        response = requests.post(
            f"{self.base_url}/register_world",
            json={"world_name": world_name}
        )
        if response.status_code != 200:
            print(f"Error: {response.json()}")
        return str(response)
    
    def register_agent(self, agent_name: str, world_name: str) -> None:
        response = requests.post(
            f"{self.base_url}/register_agent",
            json={"agent_name": agent_name, "world_name": world_name}
        )
        return str(response)
    
    def export_history(self, world_name: str, limit: int = 100):
        response = requests.get(
            f"{self.base_url}/export_history",
            json={"world_name": world_name, "limit": limit}
        )
        return str(response)
    
    def export_agent_logs(self, world_name: str):
        response = requests.get(
            f"{self.base_url}/export_agent_logs",
            json={"world_name": world_name}
        )
        return str(response)
    
    def stop(self):
        """Stop the server"""
        if self.server:
            self.server.stop() 