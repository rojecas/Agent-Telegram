# tools/telegram_tool.py

import os
import json
import requests
from typing import Dict, Any, List, Optional
from tools.registry import tool
from dotenv import load_dotenv

# Asegurar que las variables de entorno estén cargadas
load_dotenv()

# Cargar token desde .env
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if TELEGRAM_BOT_TOKEN:
    print(f"[DEBUG] Telegram token cargado: {TELEGRAM_BOT_TOKEN[:10]}...")
else:
    print("[DEBUG] Telegram token NO cargado")

# URL base de la API de Telegram
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# --- Herramienta: Enviar mensaje por Telegram (telegram_send) ---
TELEGRAM_SEND_SCHEMA = {
    "description": "Envía un mensaje de texto a un chat de Telegram. Úsala cuando el usuario solicite enviar un mensaje, notificación o respuesta a través de Telegram.",
    "parameters": {
        "type": "object",
        "properties": {
            "chat_id": {
                "type": "string",
                "description": "ID del chat de Telegram (puede ser un número o un username con @). Si no se proporciona, se usará el CHAT_ID por defecto del entorno."
            },
            "text": {
                "type": "string",
                "description": "Texto del mensaje a enviar. Puede incluir formato Markdown básico."
            },
            "parse_mode": {
                "type": "string",
                "description": "Modo de parseo para formato: 'MarkdownV2', 'HTML', o 'Markdown' (legacy). Por defecto: 'MarkdownV2'.",
                "enum": ["MarkdownV2", "HTML", "Markdown"]
            }
        },
        "required": ["text"]
    }
}

@tool(schema=TELEGRAM_SEND_SCHEMA)
def telegram_send(text: str, chat_id: Optional[str] = None, parse_mode: str = "MarkdownV2") -> Dict[str, Any]:
    """
    Envía un mensaje de texto a un chat de Telegram.
    """
    print(f"  [TOOL] Herramienta llamada: telegram_send (chat_id={chat_id})")
    
    if not TELEGRAM_BOT_TOKEN:
        return {
            "success": False,
            "error": "Token de bot de Telegram no configurado. Agregue TELEGRAM_BOT_TOKEN al archivo .env"
        }
    
    # Determinar chat_id: usar el proporcionado o el del entorno
    target_chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
    if not target_chat_id:
        return {
            "success": False,
            "error": "Se requiere chat_id. Proporcione un chat_id o configure TELEGRAM_CHAT_ID en .env"
        }
    
    # Preparar payload
    payload = {
        "chat_id": target_chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    
    try:
        response = requests.post(f"{TELEGRAM_API_BASE}/sendMessage", json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get("ok"):
            return {
                "success": True,
                "message": "Mensaje enviado exitosamente",
                "message_id": result["result"]["message_id"],
                "chat_id": result["result"]["chat"]["id"]
            }
        else:
            return {
                "success": False,
                "error": f"Error de Telegram API: {result.get('description', 'Unknown error')}"
            }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Error de conexión: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error inesperado: {str(e)}"
        }

# --- Herramienta: Recibir mensajes de Telegram (telegram_receive) ---
TELEGRAM_RECEIVE_SCHEMA = {
    "description": "Obtiene los últimos mensajes recibidos en el bot de Telegram. Úsala para leer mensajes nuevos de los usuarios. Puedes especificar cuántos mensajes obtener y de qué chat.",
    "parameters": {
        "type": "object",
        "properties": {
            "chat_id": {
                "type": "string",
                "description": "ID del chat de Telegram (opcional). Si se especifica, solo se obtienen mensajes de ese chat. Si no, se obtienen mensajes de todos los chats."
            },
            "limit": {
                "type": "integer",
                "description": "Número máximo de mensajes a obtener (por defecto 10, máximo 100).",
                "minimum": 1,
                "maximum": 100
            },
            "offset": {
                "type": "integer",
                "description": "Identificador del update más antiguo que se debe obtener. Usar -1 para obtener solo mensajes nuevos (por defecto -1)."
            }
        },
        "required": []
    }
}

@tool(schema=TELEGRAM_RECEIVE_SCHEMA)
def telegram_receive(chat_id: Optional[str] = None, limit: int = 10, offset: int = -1) -> Dict[str, Any]:
    """
    Obtiene los últimos mensajes recibidos en el bot de Telegram.
    Si offset es -1, se usa el último update_id almacenado (no implementado persistentemente).
    """
    print(f"  [TOOL] Herramienta llamada: telegram_receive (chat_id={chat_id}, limit={limit})")
    
    if not TELEGRAM_BOT_TOKEN:
        return {
            "success": False,
            "error": "Token de bot de Telegram no configurado. Agregue TELEGRAM_BOT_TOKEN al archivo .env"
        }
    
    # En una implementación real, deberíamos almacenar el último update_id procesado
    # para evitar repetir mensajes. Por ahora, usamos offset=0 para obtener todos los updates.
    # Si offset es -1, usaremos 0 (simple).
    params = {
        "limit": limit,
        "offset": 0 if offset == -1 else offset
    }
    
    try:
        response = requests.get(f"{TELEGRAM_API_BASE}/getUpdates", params=params, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if not result.get("ok"):
            return {
                "success": False,
                "error": f"Error de Telegram API: {result.get('description', 'Unknown error')}"
            }
        
        updates = result.get("result", [])
        filtered_updates = []
        for update in updates:
            # Filtrar por chat_id si se especifica
            if "message" in update:
                message = update["message"]
                msg_chat_id = str(message["chat"]["id"])
                if chat_id and msg_chat_id != chat_id:
                    continue
                filtered_updates.append({
                    "update_id": update["update_id"],
                    "message_id": message["message_id"],
                    "chat_id": msg_chat_id,
                    "from": message.get("from", {}).get("first_name", "Unknown"),
                    "text": message.get("text", ""),
                    "date": message.get("date")
                })
        
        # Ordenar por update_id (más antiguo primero)
        filtered_updates.sort(key=lambda x: x["update_id"])
        
        return {
            "success": True,
            "count": len(filtered_updates),
            "updates": filtered_updates,
            "latest_update_id": filtered_updates[-1]["update_id"] if filtered_updates else 0
        }
    
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Error de conexión: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error inesperado: {str(e)}"
        }

# --- Herramienta: Configurar webhook (telegram_set_webhook) ---
TELEGRAM_SET_WEBHOOK_SCHEMA = {
    "description": "Configura un webhook para que Telegram envíe automáticamente los mensajes a una URL especificada. Úsala si deseas recibir mensajes en tiempo real.",
    "parameters": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL HTTPS donde Telegram enviará las actualizaciones. Debe ser pública y válida."
            },
            "secret_token": {
                "type": "string",
                "description": "Token secreto para verificar la autenticidad de las peticiones (opcional)."
            }
        },
        "required": ["url"]
    }
}

@tool(schema=TELEGRAM_SET_WEBHOOK_SCHEMA)
def telegram_set_webhook(url: str, secret_token: Optional[str] = None) -> Dict[str, Any]:
    """
    Configura un webhook para el bot de Telegram.
    """
    print(f"  [TOOL] Herramienta llamada: telegram_set_webhook (url={url})")
    
    if not TELEGRAM_BOT_TOKEN:
        return {
            "success": False,
            "error": "Token de bot de Telegram no configurado."
        }
    
    payload = {"url": url}
    if secret_token:
        payload["secret_token"] = secret_token
    
    try:
        response = requests.post(f"{TELEGRAM_API_BASE}/setWebhook", json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get("ok"):
            return {
                "success": True,
                "message": "Webhook configurado exitosamente",
                "result": result.get("result", "")
            }
        else:
            return {
                "success": False,
                "error": f"Error de Telegram API: {result.get('description', 'Unknown error')}"
            }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Error de conexión: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error inesperado: {str(e)}"
        }

# --- Herramienta: Obtener información del bot (telegram_get_me) ---
TELEGRAM_GET_ME_SCHEMA = {
    "description": "Obtiene información básica del bot de Telegram (nombre, username, ID). Úsala para verificar que el bot esté configurado correctamente.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

@tool(schema=TELEGRAM_GET_ME_SCHEMA)
def telegram_get_me() -> Dict[str, Any]:
    """
    Obtiene información del bot.
    """
    print("  [TOOL] Herramienta llamada: telegram_get_me")
    
    if not TELEGRAM_BOT_TOKEN:
        return {
            "success": False,
            "error": "Token de bot de Telegram no configurado."
        }
    
    try:
        response = requests.get(f"{TELEGRAM_API_BASE}/getMe", timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get("ok"):
            bot_info = result["result"]
            return {
                "success": True,
                "bot_info": {
                    "id": bot_info["id"],
                    "first_name": bot_info.get("first_name"),
                    "username": bot_info.get("username"),
                    "can_join_groups": bot_info.get("can_join_groups"),
                    "can_read_all_group_messages": bot_info.get("can_read_all_group_messages"),
                    "supports_inline_queries": bot_info.get("supports_inline_queries")
                }
            }
        else:
            return {
                "success": False,
                "error": f"Error de Telegram API: {result.get('description', 'Unknown error')}"
            }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Error de conexión: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error inesperado: {str(e)}"
        }