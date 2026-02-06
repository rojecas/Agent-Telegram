# tools/telegram_tool.py

import os
import json
import requests
from typing import Dict, Any, List, Optional
from .registry import tool
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

def _log_telegram_response(method: str, response: requests.Response):
    """Auxiliar para imprimir detalles de la respuesta de Telegram en modo desarrollo."""
    if os.getenv("APP_STATUS") == "development":
        status = response.status_code
        try:
            body = response.json()
        except:
            body = response.text
            
        print(f"  📡 [TELEGRAM API] {method} | Status: {status}")
        if not response.ok:
            print(f"  ⚠️  Error Body: {json.dumps(body, indent=2, ensure_ascii=False)}")
        elif method != "getUpdates": # No saturar con cada poll exitoso
            print(f"  ✅ Response: {json.dumps(body, indent=2, ensure_ascii=False)}")

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
def telegram_send(text: str, chat_id: Optional[str] = None, parse_mode: str = "MarkdownV2", **kwargs) -> Dict[str, Any]:
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
        _log_telegram_response("sendMessage", response)
        
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

# @tool(schema=TELEGRAM_RECEIVE_SCHEMA) # Deshabilitado para evitar conflictos con el polling en segundo plano
def telegram_receive(chat_id: Optional[str] = None, limit: int = 10, offset: int = -1, timeout: int = 30, **kwargs) -> Dict[str, Any]:
    """
    Recibe mensajes de Telegram usando polling.
    Utiliza 'timeout' para Long Polling (el servidor mantiene la conexión abierta).
    """
    print(f"  [TOOL] Herramienta llamada: telegram_receive (limit={limit}, offset={offset}, timeout={timeout})")
    
    if not TELEGRAM_BOT_TOKEN:
        return {"success": False, "error": "Token de Telegram no configurado"}
    
    # En una implementación real, deberíamos almacenar el último update_id procesado
    # para evitar repetir mensajes. Por ahora, usamos offset=0 para obtener todos los updates.
    # Si offset es -1, usaremos 0 (simple).
    params = {
        "limit": limit,
        "offset": 0 if offset == -1 else offset,
        "timeout": timeout  # Long Polling en el servidor de Telegram
    }
    
    try:
        # El timeout de requests debe ser un poco mayor que el de Telegram
        response = requests.get(f"{TELEGRAM_API_BASE}/getUpdates", params=params, timeout=timeout + 5)
        _log_telegram_response("getUpdates", response)
        
        result = response.json()
        
        if not result.get("ok"):
            # Proactivo: Si es 409, probablemente hay un webhook activo
            if response.status_code == 409:
                print("  💡 [HINT] Error 409 detectado. Intentando eliminar webhook previo...")
                requests.post(f"{TELEGRAM_API_BASE}/deleteWebhook")
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
def telegram_set_webhook(url: str, secret_token: Optional[str] = None, **kwargs) -> Dict[str, Any]:
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
        _log_telegram_response("setWebhook", response)
        
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
def telegram_get_me(**kwargs) -> Dict[str, Any]:
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
        _log_telegram_response("getMe", response)
        
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
    
# --- Herramienta: Obtener información de un chat (telegram_get_chat_info) ---
TELEGRAM_GET_CHAT_INFO_SCHEMA = {
    "description": "Obtiene información detallada de un chat de Telegram (ID, título, descripción, tipo, número de miembros y administradores). Úsala para conocer mejor el contexto de un grupo o canal.",
    "parameters": {
        "type": "object",
        "properties": {
            "chat_id": {
                "type": "string",
                "description": "ID del chat de Telegram."
            }
        },
        "required": ["chat_id"]
    }
}

@tool(schema=TELEGRAM_GET_CHAT_INFO_SCHEMA)
def telegram_get_chat_info(chat_id: str, **kwargs) -> Dict[str, Any]:
    """
    Obtiene información de un chat específico.
    """
    print(f"  [TOOL] Herramienta llamada: telegram_get_chat_info (chat_id={chat_id})")
    
    context = kwargs.get('context')
    is_group = context.is_group() if context else False

    # 🛡️ FIREWALL: En grupos, solo permitimos info del propio grupo o canales públicos
    # (Los IDs de personas son positivos, los de grupos son negativos)
    try:
        target_chat_id_int = int(chat_id)
        if is_group:
            # Si el target es una persona (ID > 0) y no es el contexto actual
            if target_chat_id_int > 0:
                 return {"success": False, "error": "Acceso denegado: No se puede consultar información privada de usuarios desde un grupo."}
            # Si el target es otro grupo diferente al actual (ID < 0)
            if str(target_chat_id_int) != str(context.chat_id):
                 # Permitimos si es canal (pero getChat dirá si es canal o no después)
                 pass
    except ValueError:
        pass # Username o algo similar, dejar pasar a la API

    if not TELEGRAM_BOT_TOKEN:
        return {"success": False, "error": "Token de Telegram no configurado"}
    
    try:
        payload = {"chat_id": chat_id}
        response = requests.post(f"{TELEGRAM_API_BASE}/getChat", json=payload, timeout=10)
        _log_telegram_response("getChat", response)
        
        result = response.json()
        
        if result.get("ok"):
            chat_info = result["result"]
            chat_type = chat_info.get("type", "unknown")
            
            summary = {
                "id": chat_info["id"],
                "type": chat_type,
                "title": chat_info.get("title"),
                "username": chat_info.get("username"),
                "first_name": chat_info.get("first_name"),
                "last_name": chat_info.get("last_name"),
                "bio": chat_info.get("bio"),
                "description": chat_info.get("description")
            }

            # Si es un grupo o canal, intentar obtener info extra
            if chat_type in ["group", "supergroup", "channel"]:
                # 1. Miembros
                try:
                    m_resp = requests.post(f"{TELEGRAM_API_BASE}/getChatMemberCount", json=payload, timeout=5)
                    if m_resp.ok:
                        summary["member_count"] = m_resp.json().get("result")
                except: pass

                # 2. Administradores
                try:
                    a_resp = requests.post(f"{TELEGRAM_API_BASE}/getChatAdministrators", json=payload, timeout=5)
                    if a_resp.ok:
                        admins = a_resp.json().get("result", [])
                        summary["administrators"] = [
                            {
                                "user_id": a["user"]["id"],
                                "name": a["user"].get("first_name", ""),
                                "status": a["status"]
                            } for a in admins
                        ]
                except: pass

            return {
                "success": True,
                "chat_info": summary
            }
        else:
            return {
                "success": False,
                "error": f"Error de Telegram API: {result.get('description', 'Unknown error')}"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}
