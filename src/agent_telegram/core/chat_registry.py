import json
import os
from datetime import datetime
from threading import Lock

REGISTRY_PATH = "assets/system/chat_registry.json"
registry_lock = Lock()

class ChatRegistry:
    @staticmethod
    def load():
        with registry_lock:
            if not os.path.exists(REGISTRY_PATH):
                return {}
            try:
                with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}

    @staticmethod
    def save(data):
        with registry_lock:
            os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
            with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def register(chat_id, source, chat_type, title=None, username=None):
        data = ChatRegistry.load()
        chat_id_str = str(chat_id)
        
        is_new = chat_id_str not in data
        
        data[chat_id_str] = {
            "chat_id": chat_id,
            "source": source,
            "type": chat_type,
            "title": title or data.get(chat_id_str, {}).get("title", ""),
            "username": username or data.get(chat_id_str, {}).get("username", ""),
            "last_seen": datetime.now().isoformat(),
            "first_seen": data.get(chat_id_str, {}).get("first_seen", datetime.now().isoformat())
        }
        
        ChatRegistry.save(data)
        return is_new

    @staticmethod
    def get_all():
        return ChatRegistry.load()
