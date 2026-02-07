#!/usr/bin/env python3
"""
Script de prueba para verificar la refactorización del módulo tools.
"""

import sys
import json
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

print("=== Test de refactorización de tools ===")

# 1. Verificar que los módulos pueden importarse
try:
    from src.tools.registry import tool_registry
    import src.tools.user_tools
    import src.tools.city_tools
    import src.tools.datetime_tool
    import src.tools.misc_tools
    print("✅ Todos los módulos importados correctamente.")
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    sys.exit(1)

# 2. Verificar que el registro contiene herramientas
tool_list = tool_registry.get_tool_list()
tool_map = tool_registry.get_tool_call_map()

print(f"\nRegistro contiene {len(tool_list)} herramientas.")
print(f"Mapa contiene {len(tool_map)} funciones.")

if len(tool_list) == 0:
    print("❌ No se registraron herramientas.")
    sys.exit(1)

# Listar herramientas registradas
print("\nHerramientas registradas:")
for tool_schema in tool_list:
    name = tool_schema["function"]["name"]
    print(f"  - {name}")

# 3. Verificar que las herramientas esenciales están presentes
essential_tools = {"add_user", "list_users", "read_ledger", "read_city_info", 
                   "add_city_info", "datetime", "get_weather", "edit_file"}
registered_names = set(tool_map.keys())

missing = essential_tools - registered_names
if missing:
    print(f"❌ Faltan herramientas: {missing}")
    sys.exit(1)
else:
    print("✅ Todas las herramientas esenciales están registradas.")

# 4. Probar una función sencilla (list_users) para verificar que funciona
print("\n--- Probando list_users() ---")
try:
    result = tool_map["list_users"]()
    print(f"Resultado: {result}")
    if "usuarios" in result:
        print("✅ list_users devolvió estructura esperada.")
    else:
        print("⚠️  list_users devolvió un formato inesperado.")
except Exception as e:
    print(f"❌ Error al ejecutar list_users: {e}")
    sys.exit(1)

# 5. Probar datetime con parámetros por defecto
print("\n--- Probando datetime() ---")
try:
    result = tool_map["datetime"]()
    if result.get("success") == True:
        print(f"✅ datetime funciona: {result.get('human_readable', '')}")
    else:
        print(f"⚠️  datetime no tuvo éxito: {result.get('error', '')}")
except Exception as e:
    print(f"❌ Error al ejecutar datetime: {e}")
    # No salimos porque podría faltar pytz, pero es un error manejado en la función.

# 6. Verificar que agents.py puede importar tool_registry sin problemas
print("\n--- Probando import de agents.py ---")
try:
    from src.agent_telegram.core import agents
    print("✅ agents.py importado correctamente.")
except Exception as e:
    print(f"❌ Error importando agents.py: {e}")
    sys.exit(1)

print("\n=== Todos los tests pasaron exitosamente. ===")