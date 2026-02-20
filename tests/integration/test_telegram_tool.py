#!/usr/bin/env python3
"""
Script de prueba para verificar que las herramientas de Telegram están registradas correctamente.
"""

import sys
import os
sys.path.insert(0, '.')

# Importar agents (que importa todas las herramientas)
import src.core.agents
from src.tools.registry import tool_registry
from src.core.logger import safe_print

print("=== Prueba de registro de herramientas de Telegram ===")
print(f"Número total de herramientas registradas: {len(tool_registry.tool_functions)}")
print("Lista de herramientas:")
for name in sorted(tool_registry.tool_functions.keys()):
    print(f"  - {name}")

# Verificar específicamente las herramientas de Telegram
telegram_tools = ['telegram_send', 'telegram_receive', 'telegram_set_webhook', 'telegram_get_me']
for tool_name in telegram_tools:
    if tool_name in tool_registry.tool_functions:
        safe_print(f"✅ {tool_name} está registrada")
    else:
        safe_print(f"❌ {tool_name} NO está registrada")

# Probar que el esquema está presente
schemas = tool_registry.get_tool_list()
telegram_schemas = [s for s in schemas if s['function']['name'] in telegram_tools]
print(f"\nEsquemas de Telegram encontrados: {len(telegram_schemas)}")

# Mostrar esquema de una herramienta (opcional)
if telegram_schemas:
    print("\nEjemplo de esquema (telegram_send):")
    for s in telegram_schemas:
        if s['function']['name'] == 'telegram_send':
            import json
            print(json.dumps(s, indent=2, ensure_ascii=False))
            break

# Verificar que las funciones son invocables
if 'telegram_get_me' in tool_registry.tool_functions:
    func = tool_registry.tool_functions['telegram_get_me']
    print(f"\nFirma de telegram_get_me: {func.__name__}")
    print(f"  Módulo: {func.__module__}")
    print(f"  ¿Es callable? {callable(func)}")
else:
    safe_print("\n⚠️  telegram_get_me no encontrada")

print("\n=== Prueba completada ===")