import requests
from typing import Dict, Any, List, Optional
from .api import Tool, Server

class Client:
    def __init__(self, 
                 host: str = "localhost", 
                 port: int = 8000,
                 slack_config: Optional[Dict[str, str]] = None):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        
        # Create and start server with same configuration
        self.server = Server(slack_config=slack_config)
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
        
    def stop(self):
        """Stop the server"""
        if self.server:
            self.server.stop() 