from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from agentslack.slack import Slack
from agentslack.registry import Registry
import threading
import uvicorn
import time

class Tool(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class Server:
    def __init__(self, slack_config: Optional[Dict[str, str]] = None):
        self.app = FastAPI()
        self.registry = Registry()
        self.slack = Slack(**slack_config if slack_config else {})
        self.tools = {
            "send_message": Tool(
                name="send_message",
                description="Send a message to a channel or user",
                parameters={
                    "message": "string",
                    "target_channel_id": "string"
                }
            )
        }
        self.server_thread = None
        self._setup_routes()
    
    def _setup_routes(self):
        @self.app.get("/tools")
        async def list_tools():
            return list(self.tools.values())
            
        @self.app.post("/tools/{tool_name}")
        async def call_tool(tool_name: str, parameters: Dict[str, Any]):
            if tool_name not in self.tools:
                raise HTTPException(status_code=404, detail="Tool not found")
                
            if tool_name == "send_message":
                response = self.slack.send_messsage(
                    message=parameters["message"],
                    target_channel_id=parameters["target_channel_id"]
                )
                
                return {"status": "success", "response": str(response)} # TODO for some reason parsing response as json throws an error, so I am returning str for now
            
            raise HTTPException(status_code=400, detail="Tool execution failed")
    
    def start(self, host: str = "0.0.0.0", port: int = 8080):
        """Start the server in a background thread"""
        if self.server_thread is not None:
            return  # Server already running
            
        def run_server():
            uvicorn.run(self.app, host=host, port=port)
            
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(1)  # Give the server a moment to start

    def stop(self):
        """Stop the server"""
        if self.server_thread is not None:
            self.server_thread.join(timeout=1)
            self.server_thread = None

    def register_world(self, name: str):
        """Helper method to register a world programmatically"""
        self.registry.register_world(name)
    
    def register_agent(self, world_name: str, agent_name: str):
        """Helper method to register an agent programmatically"""
        app_response = self.slack.create_app(
            app_name=agent_name,
            app_description=f"Agent {agent_name} in world {world_name}"
        )
        slack_app_id = app_response["app_id"]
        self.registry.register_agent(agent_name, world_name, slack_app_id)

if __name__ == "__main__":
    server = Server()
    server.start()
