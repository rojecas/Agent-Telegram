
import unittest
import sys
import os
import queue

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.tools.registry import tool_registry
from src.core.skill_manager import skill_manager, request_skill_activation

class TestDynamicLoading(unittest.TestCase):
    def test_initial_registry_state(self):
        """Verifica que está la herramienta maestra."""
        tools = tool_registry.get_tool_list()
        tool_names = [t["function"]["name"] for t in tools]
        
        self.assertIn("request_skill_activation", tool_names)

    def test_skill_activation(self):
        """Verifica que activar un skill carga las herramientas correspondientes."""
        # Activamos el skill 'utility' (contiene datetime_tool, etc)
        success = skill_manager.activate_skill("utility")
        self.assertTrue(success)
        
        tools = tool_registry.get_tool_list()
        tool_names = [t["function"]["name"] for t in tools]
        
        # Ahora debería estar 'datetime' (de datetime_tool)
        self.assertIn("datetime", tool_names)
        self.assertIn("read_city_info", tool_names)
        
    def test_request_skill_activation_tool(self):
        """Verifica que la herramienta maestra funciona correctamente."""
        # Probamos activar 'system' a través de la herramienta
        result = request_skill_activation(skill_name="system")
        self.assertIn("activado con éxito", result)
        
        tools = tool_registry.get_tool_list()
        tool_names = [t["function"]["name"] for t in tools]
        self.assertIn("list_active_chats", tool_names)

if __name__ == "__main__":
    unittest.main()
