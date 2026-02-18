import os
import json
from openai import OpenAI
from src.core.persistence.history_manager import HISTORY_DIR, HistoryManager
from dotenv import load_dotenv

load_dotenv()

class MemoryConsolidator:
    def __init__(self, client: OpenAI):
        self.client = client

    def consolidate_chat(self, chat_id):
        """Usa el LLM para limpiar el historial de un chat específico."""
        history = HistoryManager.load_history(chat_id, limit=100)
        if not history:
            return

        print(f"🧹 Consolidando memoria del chat {chat_id} ({len(history)} mensajes)...")

        # Formatear el historial para el prompt
        formatted_history = ""
        for i, msg in enumerate(history):
            formatted_history += f"[{i}] {msg['role'].upper()}: {msg['content']}\n"

        prompt = f"""Tu tarea es limpiar los archivos de log de una conversación para mantener solo el contexto RELEVANTE.
REGLAS:
1. Elimina saludos simples ("hola", "buenos días") si no contienen información extra.
2. Elimina confirmaciones vacías ("entendido", "ok", "perfecto").
3. Elimina ruidos de conversación que no aporten hechos, preferencias o contexto del problema.
4. MANTÉN los hechos, datos técnicos, solicitudes de usuario, respuestas útiles y contexto emocional relevante.
5. Devuelve EXCLUSIVAMENTE una lista JSON de los índices [i] que debemos MANTENER.

EJEMPLO DE SALIDA: [2, 4, 5, 8, 9]

HISTORIAL A PROCESAR:
{formatted_history}
"""

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat", # O el modelo que estés usando
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                response_format=None  # DeepSeek API no requiere formato JSON forzado; usamos regex para extraer la lista
            )
            
            # Procesar respuesta para extraer la lista de índices
            content = response.choices[0].message.content
            # Intentar encontrar los corchetes si no es JSON puro
            import re
            match = re.search(r'\[.*\]', content)
            if match:
                indices = json.loads(match.group(0))
                
                # Crear nuevo historial filtrado
                new_history = [history[i] for i in indices if i < len(history)]
                
                # Guardar el historial "limpio"
                HistoryManager.save_history(chat_id, new_history)
                print(f"✅ Limpieza completada. De {len(history)} mensajes quedan {len(new_history)}.")
            else:
                print(f"⚠️ No se pudo interpretar la respuesta del LLM para {chat_id}")
        
        except Exception as e:
            print(f"❌ Error consolidando chat {chat_id}: {e}")

def consolidate_all_histories(client: OpenAI):
    """Itera por todos los archivos de historial y los consolida."""
    if not os.path.exists(HISTORY_DIR):
        return

    consolidator = MemoryConsolidator(client)
    files = [f for f in os.listdir(HISTORY_DIR) if f.endswith(".json")]
    
    if not files:
        print("📭 No hay historiales que consolidar.")
        return

    print(f"\n🧠 Iniciando Consolidación de Memoria Automática para {len(files)} chats...")
    for filename in files:
        chat_id = filename.replace(".json", "")
        consolidator.consolidate_chat(chat_id)
    print("✨ Consolidación terminada.\n")
