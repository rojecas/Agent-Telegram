import json
import os
import re
from openai import OpenAI
from src.core.persistence.history_manager import HistoryManager, HISTORY_DIR
from src.tools.user_tools import update_user_info
from src.tools.city_tools import add_city_info

class IntelligenceExtractor:
    def __init__(self, client: OpenAI):
        self.client = client

    def extract_and_persist(self, chat_id):
        """Analiza la sesión de un chat y extrae información útil."""
        # Cargar historial reciente (ej: últimos 100 mensajes)
        history = HistoryManager.load_history(chat_id, limit=100)
        if not history:
            return

        print(f"🔍 Extrayendo inteligencia del chat {chat_id}...")

        # Formatear historial
        formatted_history = ""
        for msg in history:
            formatted_history += f"{msg['role'].upper()}: {msg['content']}\n"

        prompt = f"""Analiza la siguiente conversación de Andrew Martin (un bot asistente) con un usuario.
Tu meta es encontrar Hechos (Facts) nuevos sobre el usuario o sobre ciudades que deban ser persistidos en sus archivos .ledger.

REGLAS DE EXTRACCIÓN:
1. Solo extrae información que sea EXPLÍCITA y RELEVANTE.
2. Formato de salida: Devuelve un objeto JSON con dos llaves: 'user_updates' y 'city_updates'.
3. 'user_updates': Lista de {{ "user": "nombre.apellido", "updates": {{...}} }}
   - Estructura: {{ "public_profile": {{ "interests": [] }}, "private_profile": {{ "goals": [] }} }}
4. 'city_updates': Lista de {{ "city": "nombre", "updates": {{...}} }}
   - CATEGORÍAS VÁLIDAS: 'atractivos_culturales', 'espacios_publicos', 'parques_y_naturaleza', 'experiencias_gastronomicas', 'unidades_deportivas', 'centros_academicos', 'centros_comerciales'.
   - CADA ITEM debe ser un objeto con al menos: {{ "nombre": "...", "descripcion": "..." }}
   - Ejemplo updates: {{ "experiencias_gastronomicas": [{{ "nombre": "Pizza Solar", "descripcion": "Excelente pizza en Cali" }}] }}

CONVERSACIÓN:
{formatted_history}

SALIDA JSON:"""

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            intel = json.loads(content)

            # Aplicar actualizaciones de usuario
            for update in intel.get("user_updates", []):
                user = update.get("user")
                info = update.get("updates")
                if user and info:
                    print(f" ✨ [EXTRACTOR] Actualizando perfil de usuario: {user}")
                    update_user_info(user=user, info_json=json.dumps(info))

            # Aplicar actualizaciones de ciudad
            for update in intel.get("city_updates", []):
                city = update.get("city")
                info = update.get("updates")
                if city and info:
                    print(f" ✨ [EXTRACTOR] Actualizando ledger de ciudad: {city}")
                    add_city_info(city=city, info_json=json.dumps(info))

        except Exception as e:
            print(f"❌ Error extrayendo inteligencia en {chat_id}: {e}")

def run_extraction_on_all(client: OpenAI):
    """Ejecuta la extracción en todos los historiales antes del cierre."""
    if not os.path.exists(HISTORY_DIR):
        return

    extractor = IntelligenceExtractor(client)
    files = [f for f in os.listdir(HISTORY_DIR) if f.endswith(".json")]
    
    if not files:
        return

    print(f"\n🧠 Iniciando Extracción de Inteligencia Post-Sesión para {len(files)} chats...")
    for filename in files:
        chat_id = filename.replace(".json", "")
        extractor.extract_and_persist(chat_id)
    print("✨ Extracción terminada.")
