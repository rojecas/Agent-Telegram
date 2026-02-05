import sys
import os
sys.path.append(os.getcwd())

from chat_registry import ChatRegistry
import json
import unittest

class TestPhase3(unittest.TestCase):
    def setUp(self):
        # Limpiar registro para pruebas
        if os.path.exists("assets/system/chat_registry.json"):
            os.remove("assets/system/chat_registry.json")

    def test_register_and_load(self):
        # Simular registro de un chat
        is_new = ChatRegistry.register("12345", "telegram", "private", username="testuser")
        self.assertTrue(is_new)
        
        # Verificar que se guardó
        chats = ChatRegistry.get_all()
        self.assertIn("12345", chats)
        self.assertEqual(chats["12345"]["username"], "testuser")
        
        # Registrar de nuevo (no debería ser nuevo)
        is_new_again = ChatRegistry.register("12345", "telegram", "private", title="Updated Title")
        self.assertFalse(is_new_again)
        
        chats_updated = ChatRegistry.get_all()
        self.assertEqual(chats_updated["12345"]["title"], "Updated Title")

    def test_group_registration(self):
        is_new = ChatRegistry.register("-987654321", "telegram", "group", title="Super Group")
        self.assertTrue(is_new)
        
        chats = ChatRegistry.get_all()
        self.assertEqual(chats["-987654321"]["type"], "group")

def test_tools_registration():
    from tools.registry import tool_registry
    import tools.system_tools
    import tools.telegram_tool
    
    schemas = tool_registry.get_tool_list()
    tool_names = [s["function"]["name"] for s in schemas]
    
    print(f"Herramientas registradas: {tool_names}")
    assert "list_active_chats" in tool_names
    assert "telegram_get_chat_info" in tool_names
    print("✅ Herramientas de Fase 3 correctamente registradas.")

if __name__ == "__main__":
    test_tools_registration()
    unittest.main()
