"""
Tools package for Andrew Martin assistant.

Only exports the registry and decorator to allow lazy loading of actual tool modules.
"""

from .registry import ToolRegistry, tool_registry, tool

__all__ = [
    "ToolRegistry",
    "tool_registry",
    "tool",
]