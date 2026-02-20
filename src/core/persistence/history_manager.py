import json
import os
from threading import Lock
from src.core.logger import safe_print

HISTORY_DIR = "assets/history"
history_lock = Lock()

class HistoryManager:
    @staticmethod
    def _get_path(chat_id):
        return os.path.join(HISTORY_DIR, f"{chat_id}.json")

    @staticmethod
    def load_history(chat_id, limit=100) -> list:
        """Carga los últimos N mensajes del historial persistente."""
        path = HistoryManager._get_path(chat_id)
        with history_lock:
            if not os.path.exists(path):
                return []
            try:
                with open(path, "r", encoding="utf-8") as f:
                    history = json.load(f)
                    return history[-limit:]
            except Exception as e:
                safe_print(f"⚠️ Error cargando historial para {chat_id}: {e}")
                return []

    @staticmethod
    def _to_dict(m):
        """Convierte un mensaje (dict o ChatCompletionMessage) a un diccionario estándar."""
        if isinstance(m, dict):
            return m
        # Es un objeto de OpenAI
        res = {"role": m.role, "content": m.content}
        if hasattr(m, "tool_calls") and m.tool_calls:
            # Opcional: Podríamos guardar tool_calls, pero el usuario pidió contexto real.
            # Por ahora mantendremos solo roles de usuario/asistente con contenido.
            pass
        return res

    @staticmethod
    def save_history(chat_id, messages, limit=100):
        """Guarda la lista de mensajes (limpiando sistema y herramientas)."""
        path = HistoryManager._get_path(chat_id)
        
        # Convertir todos a dict y filtrar solo user/assistant con contenido
        processed_msgs = []
        for m in messages:
            d = HistoryManager._to_dict(m)
            if d.get("role") in ["user", "assistant"] and d.get("content"):
                processed_msgs.append(d)
        
        # Mantener solo los últimos limit
        persistent_msgs = processed_msgs[-limit:]
        
        with history_lock:
            os.makedirs(HISTORY_DIR, exist_ok=True)
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(persistent_msgs, f, indent=2, ensure_ascii=False)
            except Exception as e:
                safe_print(f"⚠️ Error guardando historial para {chat_id}: {e}")

    @staticmethod
    def add_message(chat_id, role, content, limit=100):
        """Añade un mensaje de forma eficiente al historial persistente."""
        history = HistoryManager.load_history(chat_id, limit=limit)
        history.append({"role": role, "content": content})
        HistoryManager.save_history(chat_id, history, limit=limit)
