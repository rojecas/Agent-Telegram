import json
from typing import Dict, Any
from src.agent_telegram.tools.registry import tool

# 1. Define the Schema
# Use clear descriptions and JSON Schema format
MY_TOOL_SCHEMA = {
    "description": "Short description of what the tool does.",
    "parameters": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Description of the first parameter."
            },
            "param2": {
                "type": "integer",
                "description": "Description of the second parameter."
            }
        },
        "required": ["param1"]
    }
}

# 2. Implement the Tool with the @tool decorator
@tool(schema=MY_TOOL_SCHEMA)
def my_tool(param1: str, param2: int = 0, **kwargs) -> Dict[str, Any]:
    """
    Standard implementation of a new tool.
    Always include **kwargs for context flexibility.
    """
    print(f"  [TOOL] Executing my_tool with {param1} and {param2}")
    
    # 3. Handle context if needed
    context = kwargs.get('context') # If it's a Telegram message, context will be present
    
    try:
        # Logic goes here
        result = {"success": True, "value": param1}
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}
