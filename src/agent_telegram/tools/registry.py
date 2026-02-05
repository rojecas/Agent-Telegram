
import inspect
from typing import List, Dict, Callable, Any

# Registro global para almacenar funciones y sus esquemas
class ToolRegistry:
    def __init__(self):
        self.tool_functions: Dict[str, Callable] = {}
        self.tool_schemas: List[Dict[str, Any]] = []
        self.tool_call_map: Dict[str, Callable] = {}
        
    def register_tool(self, func: Callable, schema: Dict[str, Any]):
        """Registra una función de herramienta y su esquema."""
        func_name = func.__name__
        
        # Validar que el nombre de la función sea único
        if func_name in self.tool_functions:
            raise ValueError(f"La herramienta '{func_name}' ya está registrada.")
            
        self.tool_functions[func_name] = func
        
        # El esquema se transforma para el formato de la API (OpenAI/DeepSeek tools)
        api_schema = {
            "type": "function",
            "function": {
                "name": func_name,
                "description": schema["description"],
                "parameters": schema["parameters"],
            }
        }
        self.tool_schemas.append(api_schema)
        self.tool_call_map[func_name] = func
        
    def get_tool_list(self) -> List[Dict[str, Any]]:
        """Devuelve la lista de esquemas de herramientas para la API del LLM."""
        return self.tool_schemas
        
    def get_tool_call_map(self) -> Dict[str, Callable]:
        """Devuelve el mapa de nombres de herramientas a funciones Python."""
        return self.tool_call_map

# Instancia global del registro
tool_registry = ToolRegistry()

def tool(schema: Dict[str, Any]):
    """
    Decorador para registrar automáticamente funciones como herramientas.
    El esquema debe contener 'description' y 'parameters'.
    """
    def decorator(func: Callable):
        # Usar el nombre de la función como nombre de la herramienta
        tool_registry.register_tool(func, schema)
        return func
    return decorator

# Exportamos las variables que agents.py necesitará
tool_list = tool_registry.get_tool_list
TOOL_CALL_MAP = tool_registry.get_tool_call_map
