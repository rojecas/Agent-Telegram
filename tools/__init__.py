"""
Tools package for Andrew Martin assistant.

Exports all tool functions and the tool registry for backward compatibility.
"""

from .registry import ToolRegistry, tool_registry, tool
from .user_tools import add_user, list_users, read_ledger
from .city_tools import read_city_info, add_city_info
from .datetime_tool import datetime
from .misc_tools import get_weather, edit_file

__all__ = [
    "ToolRegistry",
    "tool_registry",
    "tool",
    "add_user",
    "list_users",
    "read_ledger",
    "read_city_info",
    "add_city_info",
    "datetime",
    "get_weather",
    "edit_file",
]