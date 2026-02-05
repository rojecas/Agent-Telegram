import os
import json
from pathlib import Path
from typing import Dict, Any
from tools.registry import tool

GROUP_ASSETS_DIR = "./assets/groups"

# --- Herramienta: Leer Ledger de Grupo (read_group_ledger) ---
READ_GROUP_LEDGER_SCHEMA = {
    "description": "Lee el ledger compartido de un grupo o proyecto. Si se llama dentro de un grupo, puede omitirse el group_id.",
    "parameters": {
        "type": "object",
        "properties": {
            "group_id": { "type": "string", "description": "ID del grupo (opcional si se está en el grupo)" }
        }
    }
}

@tool(schema=READ_GROUP_LEDGER_SCHEMA)
def read_group_ledger(group_id: str = None, **kwargs) -> str:
    context = kwargs.get('context')
    # Si no se da group_id, intentar obtenerlo del contexto
    if not group_id and context:
        group_id = context.chat_id
    
    if not group_id:
        return json.dumps({"error": "No se proporcionó group_id y no hay contexto de grupo."})

    print(f"  ⚙️ Herramienta llamada: read_group_ledger para '{group_id}'")
    
    file_path = os.path.join(GROUP_ASSETS_DIR, f"{group_id}.ledger")
    
    if not os.path.exists(file_path):
        # Si no existe, devolver una estructura vacía sugerida
        return json.dumps({
            "message": "No existe un ledger para este grupo aún. Se puede crear uno nuevo.",
            "group_id": group_id
        })

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.dumps(json.load(f), indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

# --- Herramienta: Actualizar Ledger de Grupo (update_group_ledger) ---
UPDATE_GROUP_LEDGER_SCHEMA = {
    "description": "Crea o actualiza información en el ledger compartido del grupo.",
    "parameters": {
        "type": "object",
        "properties": {
            "group_id": { "type": "string", "description": "ID del grupo" },
            "key": { "type": "string", "description": "Campo a actualizar (ej. 'shared_plan', 'destination')" },
            "value": { "type": "string", "description": "Valor o JSON string con la información" }
        },
        "required": ["key", "value"]
    }
}

@tool(schema=UPDATE_GROUP_LEDGER_SCHEMA)
def update_group_ledger(key: str, value: str, group_id: str = None, **kwargs) -> str:
    context = kwargs.get('context')
    if not group_id and context:
        group_id = context.chat_id

    if not group_id:
        return json.dumps({"error": "No se puede actualizar sin un group_id."})

    print(f"  ⚙️ Herramienta llamada: update_group_ledger para '{group_id}'")
    
    os.makedirs(GROUP_ASSETS_DIR, exist_ok=True)
    file_path = os.path.join(GROUP_ASSETS_DIR, f"{group_id}.ledger")

    data = {}
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    # Procesar el valor (si es JSON, convertirlo)
    try:
        processed_value = json.loads(value)
    except:
        processed_value = value

    data[key] = processed_value
    
    # Asegurar metadatos básicos
    if "group_metadata" not in data:
        data["group_metadata"] = {"group_id": group_id, "last_update": ""}
    data["group_metadata"]["last_update"] = str(os.getenv("CURRENT_TIME", "now"))

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return json.dumps({"success": True, "message": f"Campo '{key}' actualizado en el ledger del grupo {group_id}."})
