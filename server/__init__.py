"""FastMCP - A more ergonomic interface for MCP servers."""

from importlib.metadata import version

from .server import Context, SlackMCP
from .utilities.types import Image

__version__ = version("mcp")
__all__ = ["SlackMCP", "Context", "Image"]