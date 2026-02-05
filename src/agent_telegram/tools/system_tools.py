import json
from typing import Dict, Any, List
from .registry import tool
from ..core.chat_registry import ChatRegistry

LIST_ACTIVE_CHATS_SCHEMA = {
    "description": "Devuelve la lista de todos los chats (privados, grupos, canales) en los que Andrew ha tenido actividad. Úsala para responder preguntas sobre con quién has hablado o qué grupos conoces.",
    "parameters": {
        "type": "object",
        "properties": {
            "source_filter": {
                "type": "string",
                "description": "Filtrar por fuente (ej: 'telegram', 'keyboard'). Opcional.",
                "enum": ["telegram", "keyboard", "whatsapp", "email"]
            }
        },
        "required": []
    }
}

@tool(schema=LIST_ACTIVE_CHATS_SCHEMA)
def list_active_chats(source_filter: str = None, **kwargs) -> str:
    """
    Consulta el Registro Central de chats.
    """
    print(f"  [TOOL] Herramienta llamada: list_active_chats (filter={source_filter})")
    
    context = kwargs.get('context')
    is_group = context.is_group() if context else False
    
    chats = ChatRegistry.get_all()
    
    filtered_chats = []
    for cid, info in chats.items():
        if source_filter and info.get("source") != source_filter:
            continue
        
        # 🛡️ FIREWALL: Si estamos en un GRUPO, ocultamos chats privados de otros
        if is_group and info.get("type") == "private":
            continue
        
        filtered_chats.append({
            "chat_id": cid,
            "type": info.get("type"),
            "source": info.get("source"),
            "title": info.get("title", ""),
            "username": info.get("username", ""),
            "last_interaction": info.get("last_seen")
        })
    
    return json.dumps({
        "total": len(filtered_chats),
        "chats": filtered_chats
    }, indent=2, ensure_ascii=False)
