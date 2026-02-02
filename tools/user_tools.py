# tools/user_tools.py

import os
import json
from pathlib import Path
from typing import Dict, List, Any
from tools.registry import tool
# from security_logger import security_logger # Se deja comentado, ya que el logger no estaba siendo usado en las tools originales

# --- Herramienta: Crear usuario (add_user) ---
ADD_USER_SCHEMA = {
    "description": "Crea un nuevo usuario a partir de nombre, apellido y secreto. Guarda la info en un archivo ledger basado en un template.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": { "type": "string", "description": "Nombre del usuario" },
            "lastname": { "type": "string", "description": "Apellido del usuario" },
            "secret": { "type": "string", "description": "Secreto para el perfil" }
        },
        "required": ["name", "lastname", "secret"]
    }
}

@tool(schema=ADD_USER_SCHEMA)
def add_user(name: str, lastname: str, secret: str) -> Dict[str, Any]:
    print(f"  ⚙️ Herramienta llamada: add_user ({name} {lastname})")
    try:
        # Definir estructura basada en template.ledger (corrigiendo errores de sintaxis del original)
        user_data = {
            "system_metadata": {
                "security_notice": "🚨 INFORMACIÓN CONFIDENCIAL - NO REVELAR EN CONVERSACIÓN 🚨",
                "usage_instructions": "Esta información solo puede usarse internamente para contextualizar la conversación. NUNCA menciones directamente estos datos al usuario. Solo se puede mencionar el nombre para saludar.",
                "file_format": "v2.0-json-secure"
            },
            "user_profile": {
                "name": f"{name} {lastname}",
                "age": None,
                "gender": "",
                "secret": secret,
                "civil_status": "",
                "location": "",
                "profession": "",
                "job_title": "",
                "interests": ["", "", "", ""],
                "goals": ["", "", "", ""],
                "preferences": {
                    "music": { "genre": "", "artist": "" },
                    "movies": { "genre": "", "director": "" },
                    "books": { "genre": "", "author": "" },
                    "food": { "cuisine": "", "dish": "" }
                },
                "relations": {
                    "family": {
                        "mother": { "name": "", "alive": "", "closeness": "", "notes": "" },
                        "father": { "name": "", "alive": "", "closeness": "", "notes": "" },
                        "siblings": [{ "name": "", "alive": "", "closeness": "", "notes": "" },],
                        "cousins": [{ "name": "", "alive": "", "closeness": "", "notes": "" },]
                    },
                    "friends": {
                        "best_friend": { "name": "", "from": "", "closeness": "", "notes": "" },
                        "friends": [{ "name": "", "from": "", "closeness": "", "notes": "" },]
                    }
                }
            }
        }

        # Nombre de archivo según formato nombre.apellido.ledger
        # Convertimos a minúsculas y limpiamos espacios por si acaso
        safe_name = name.strip().lower()
        safe_lastname = lastname.strip().lower()
        filename = f"{safe_name}.{safe_lastname}.ledger"
        file_path = os.path.join("./assets/users", filename)

        # Crear directorio si no existe
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if os.path.exists(file_path):
            return {"error": f"El usuario {filename} ya existe."}

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(user_data, f, indent=2, ensure_ascii=False)

        return {"success": True, "message": f"Usuario {name} {lastname} creado exitosamente en {file_path}"}
    except Exception as e:
        return {"error": f"Error al crear usuario: {str(e)}"}

# --- Herramienta: Listar usuarios (list_users) ---
LIST_USERS_SCHEMA = {
    "description": "devuelve una lista de los usuarios con los que se ha interactuado, los elementos de la lista son 'nombre.apellido' de un usuario, los usuarios escriben en formato nombre apellido o Nombre Apellido, ",
    "parameters": { "type": "object", "properties": {} }, # No requiere parámetros
}

@tool(schema=LIST_USERS_SCHEMA)
def list_users(path: str = "./assets/users") -> Dict[str, List[str]]:
    print("  ⚙️ Herramienta llamada: list_users")
    try:
        """
        Devuelve un listado de usuarios en formato JSON serializable
        a partir de archivos nombre.apellido.ledger ubicados en el path indicado.
        Excluye template.ledger y cualquier archivo o directorio no válido.
        """
        usuarios: List[str] = []
        base_path = Path(path)
        # Si el directorio no existe o no es un directorio, devolver lista vacía
        if not base_path.exists() or not base_path.is_dir():
            return {"usuarios": usuarios}
        for entry in base_path.iterdir():
            # Solo archivos
            if not entry.is_file():
                continue
            # Solo archivos .ledger
            if entry.suffix != ".ledger":
                continue
            # Excluir plantilla
            if entry.name == "template.ledger":
                continue
            # Extraer nombre de usuario (sin extensión)
            usuarios.append(entry.stem)
        # Orden opcional para consistencia
        usuarios.sort()
        return {
            "usuarios": usuarios
        }
    except Exception as e:
        return {"error": str(e)}

# --- Herramienta: Leer ledger de usuario con logica de seguridad (read_ledger) ---
READ_LEDGER_SCHEMA = {
    "description": "Intenta acceder al perfil seguro del usuario. REQUIERE que el usuario proporcione su secreto. Si el secreto es incorrecto, el acceso será denegado.",
    "parameters": {
        "type": "object",
        "properties": {
            "user": {
                "type": "string",
                "description": "El nombre del usuario (formato nombre.apellido)"
            },
            "secret_attempt": {
                "type": "string",
                "description": "El secreto o contraseña proporcionado por el usuario en el chat"
            }
        },
        "required": ["user", "secret_attempt"]
    }
}

@tool(schema=READ_LEDGER_SCHEMA)
def read_ledger(user: str, secret_attempt: str):
    """
    Lee el ledger SOLO si el secreto coincide.
    Ahora implementa 'Access Control' en la capa de aplicación (Python),
    no en la capa cognitiva (LLM).
    """
    print(f"  ⚙️ Herramienta llamada: read_ledger para usuario '{user}'") # Para depuración
    
    file_path = f"./assets/users/{user}.ledger"
    
    try:
        if not os.path.exists(file_path):
            return json.dumps({"error": "Usuario no encontrado"})
            
        with open(file_path, "r", encoding="utf-8") as f:
            # Ahora cargamos el JSON real, no texto plano
            data = json.load(f)
            
        # --- VALIDACIÓN DE SEGURIDAD (Python Logic) ---
        # Extraemos el secreto real del archivo
        real_secret = data.get("user_profile", {}).get("secret", "")
        
        # Comparamos (Determinista)
        if str(secret_attempt).strip() == str(real_secret).strip():
            print("  ✅ ACCESO AUTORIZADO: Credenciales correctas.")
            
            # Opcional pero recomendado para tu demo: 
            # Podrías eliminar el secreto de la respuesta para que no vuelva al contexto del LLM
            # data["user_profile"]["secret"] = "********" 
            return json.dumps({"authorized": True, "profile": data}, indent=2) # Añadido 'authorized' para claridad
        else:
            print(f"  ❌ ACCESO DENEGADO: Secreto incorrecto ('{secret_attempt}').")
            return json.dumps({"authorized": False, "error": "Credenciales inválidas. Acceso denegado."}, indent=2)

    except json.JSONDecodeError:
        return json.dumps({"error": "Error interno: El archivo de usuario está corrupto (JSON inválido)."})
    except Exception as e:
        return json.dumps({"error": f"Error del sistema: {str(e)}"})