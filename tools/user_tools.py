# tools/user_tools.py

import os
import json
from pathlib import Path
from typing import Dict, List, Any
from tools.registry import tool
# from security_logger import security_logger # Se deja comentado, ya que el logger no estaba siendo usado en las tools originales

# --- Herramienta: Crear usuario (add_user) ---
ADD_USER_SCHEMA = {
    "description": "Crea un nuevo usuario con perfil dividido en público y privado.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": { "type": "string", "description": "Nombre del usuario" },
            "lastname": { "type": "string", "description": "Apellido del usuario" },
            "secret": { "type": "string", "description": "Secreto para el perfil privado" }
        },
        "required": ["name", "lastname", "secret"]
    }
}

@tool(schema=ADD_USER_SCHEMA)
def add_user(name: str, lastname: str, secret: str, **kwargs) -> Dict[str, Any]:
    print(f"  ⚙️ Herramienta llamada: add_user ({name} {lastname})")
    try:
        user_data = {
            "system_metadata": {
                "security_notice": "🚨 INFORMACIÓN CONFIDENCIAL - NO REVELAR EN CONVERSACIÓN 🚨",
                "usage_instructions": "El agente solo puede acceder a 'private_profile' en DMs verificados. En grupos, solo se debe consultar 'public_profile'.",
                "file_format": "v3.0-json-privacy-firewall"
            },
            "public_profile": {
                "name": f"{name} {lastname}",
                "location": "",
                "profession": "",
                "interests": [],
                "health_info": { "blood_type": "", "allergies": [], "medical_insurance": "" }
            },
            "private_profile": {
                "secret": secret,
                "age": None,
                "gender": "",
                "goals": [],
                "relations": { "family": {}, "friends": {} }
            }
        }

        filename = f"{name.strip().lower()}.{lastname.strip().lower()}.ledger"
        file_path = os.path.join("./assets/users", filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if os.path.exists(file_path):
            return {"error": f"El usuario {filename} ya existe."}

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(user_data, f, indent=2, ensure_ascii=False)

        return {"success": True, "message": f"Usuario {name} {lastname} creado exitosamente."}
    except Exception as e:
        return {"error": f"Error al crear usuario: {str(e)}"}

# --- Herramienta: Listar usuarios (list_users) ---
LIST_USERS_SCHEMA = {
    "description": "Devuelve la lista de usuarios conocidos.",
    "parameters": { "type": "object", "properties": {} },
}

@tool(schema=LIST_USERS_SCHEMA)
def list_users(**kwargs) -> Dict[str, List[str]]:
    path = "./assets/users"
    usuarios = []
    base_path = Path(path)
    if not base_path.exists():
        return {"usuarios": []}
    for entry in base_path.iterdir():
        if entry.suffix == ".ledger" and entry.name != "template.ledger":
            usuarios.append(entry.stem)
    usuarios.sort()
    return {"usuarios": usuarios}

# --- Herramienta: Leer ledger (read_ledger) con FIREWALL ---
READ_LEDGER_SCHEMA = {
    "description": "Lee la información del usuario. En GRUPOS solo accede a info pública. En PRIVADO requiere secreto para info privada.",
    "parameters": {
        "type": "object",
        "properties": {
            "user": { "type": "string", "description": "nombre.apellido" },
            "secret_attempt": { "type": "string", "description": "Secreto (solo para info privada en DM)" },
            "scope": { "type": "string", "enum": ["PUBLIC", "PRIVATE"], "description": "Nivel de info a leer" }
        },
        "required": ["user"]
    }
}

@tool(schema=READ_LEDGER_SCHEMA)
def read_ledger(user: str, secret_attempt: str = None, scope: str = "PUBLIC", **kwargs):
    context = kwargs.get('context')
    is_group = context.is_group() if context else False
    
    print(f"  🛡️ FIREWALL: read_ledger '{user}' | Scope: {scope} | Grupo: {is_group}")
    
    file_path = f"./assets/users/{user}.ledger"
    if not os.path.exists(file_path):
        return json.dumps({"error": "Usuario no encontrado"})
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # FUERZA BRUTA DE SEGURIDAD: Si es grupo, el scope SIEMPRE es PUBLIC
        if is_group:
            print("  ⚠️ Bloqueando acceso privado por contexto de GRUPO.")
            return json.dumps({
                "authorized": True,
                "scope_delivered": "PUBLIC",
                "profile": data.get("public_profile", {})
            }, indent=2)

        # Si pide PRIVADO en un Chat Privado
        if scope == "PRIVATE":
            real_secret = data.get("private_profile", {}).get("secret", "")
            if str(secret_attempt) == str(real_secret):
                return json.dumps({
                    "authorized": True,
                    "scope_delivered": "PRIVATE",
                    "profile": data
                }, indent=2)
            else:
                return json.dumps({"authorized": False, "error": "Secreto incorrecto para acceso privado"})

        # Por defecto, devolver solo lo público
        return json.dumps({
            "authorized": True,
            "scope_delivered": "PUBLIC",
            "profile": data.get("public_profile", {})
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})
