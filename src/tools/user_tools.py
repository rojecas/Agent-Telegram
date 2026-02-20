# tools/user_tools.py

import os
import json
from pathlib import Path
from typing import Dict, List, Any
from .registry import tool
from src.core.utils import benchmark, debug_print
from src.core.logger import safe_print
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
    debug_print(f"  [TOOL] Herramienta llamada: add_user ({name} {lastname})")
    try:
        user_data = {
            "system_metadata": {
                "security_notice": "🚨 INFORMACIÓN CONFIDENCIAL - NO REVELAR EN CONVERSACIÓN 🚨",
                "usage_instructions": "El agente solo puede acceder a 'private_profile' en DMs verificados. En grupos, solo se debe consultar 'public_profile'.",
                "file_format": "v3.0-json-privacy-firewall"
            },
            "public_profile": {
                "name": f"{name} {lastname}".strip(),
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

        # Lógica de Sanitización y Estandarización de Nombre de Archivo
        # 1. Limpieza básica
        n_tokens = name.strip().lower().split()
        l_tokens = lastname.strip().lower().split()

        # 2. Extracción de Primer Nombre y Primer Apellido
        # Si no hay nombre, usar "unknown".
        fname = n_tokens[0] if n_tokens else "unknown"
        
        # Si hay apellido explícito, usar el primero. 
        # Si no, intentar sacar el último token del nombre (si hay más de uno).
        if l_tokens:
            lname = l_tokens[0]
        elif len(n_tokens) > 1:
            lname = n_tokens[-1]
        else:
            lname = "unknown"

        # 3. Construcción del nombre base
        base_filename = f"{fname}.{lname}" # Ej: juan.perez

        # 4. Manejo de Homónimos (Consecutivos)
        users_dir = "./assets/users"
        os.makedirs(users_dir, exist_ok=True)
        
        filename = f"{base_filename}.ledger"
        counter = 0
        
        # Bucle para encontrar un nombre libre: juan.perez.ledger -> juan.perez.1.ledger -> juan.perez.2.ledger
        while os.path.exists(os.path.join(users_dir, filename)):
            counter += 1
            filename = f"{base_filename}.{counter}.ledger"

        file_path = os.path.join(users_dir, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(user_data, f, indent=2, ensure_ascii=False)

        return {"success": True, "message": f"Usuario {name} {lastname} creado exitosamente. Archivo: {filename}"}
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

@benchmark
@tool(schema=READ_LEDGER_SCHEMA)
def read_ledger(user: str, secret_attempt: str = None, scope: str = "PUBLIC", **kwargs):
    context = kwargs.get('context')
    is_group = context.is_group() if context else False
    
    safe_print(f"  🛡️ FIREWALL: read_ledger '{user}' | Scope: {scope} | Grupo: {is_group}")
    
    file_path = f"./assets/users/{user}.ledger"
    if not os.path.exists(file_path):
        return json.dumps({"error": "Usuario no encontrado"})
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # FUERZA BRUTA DE SEGURIDAD: Si es grupo, el scope SIEMPRE es PUBLIC
        if is_group:
            safe_print("  ⚠️ Bloqueando acceso privado por contexto de GRUPO.")
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

# --- Herramienta: Actualizar información de usuario (update_user_info) ---
UPDATE_USER_INFO_SCHEMA = {
    "description": "Actualiza o agrega información al perfil de un usuario. Úsala para guardar metas, intereses, o datos personales descubiertos en la conversación. No sobrescribe el perfil completo, solo las secciones especificadas.",
    "parameters": {
        "type": "object",
        "properties": {
            "user": { "type": "string", "description": "nombre.apellido" },
            "info_json": {
                "type": "string",
                "description": "JSON String con campos a actualizar. Ejemplo: {'public_profile': {'interests': ['café']}, 'private_profile': {'goals': ['viajar']}}"
            }
        },
        "required": ["user", "info_json"]
    }
}

@benchmark
@tool(schema=UPDATE_USER_INFO_SCHEMA)
def update_user_info(user: str, info_json: str, **kwargs):
    debug_print(f"  [TOOL] Herramienta llamada: update_user_info ({user})")
    try:
        file_path = f"./assets/users/{user}.ledger"
        if not os.path.exists(file_path):
            return json.dumps({"error": f"No se encontró el ledger para el usuario {user}"})

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        try:
            updates = json.loads(info_json)
        except json.JSONDecodeError:
            return json.dumps({"error": "info_json no es un JSON válido"})

        def deep_merge(target, source):
            for key, value in source.items():
                if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                    deep_merge(target[key], value)
                elif isinstance(value, list) and key in target and isinstance(target[key], list):
                    # Combinar listas sin duplicados si son strings/simples
                    for item in value:
                        if item not in target[key]:
                            target[key].append(item)
                else:
                    target[key] = value

        deep_merge(data, updates)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return json.dumps({"success": True, "message": f"Perfil de {user} actualizado correctamente"})

    except Exception as e:
        return json.dumps({"error": f"Error al actualizar usuario: {str(e)}"})
