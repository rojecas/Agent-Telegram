import os
import sys
import json
from openai import OpenAI
from dotenv import load_dotenv
from src.core.logger import safe_print

# Añadir el directorio raíz al path
sys.path.append(os.getcwd())

from src.core.persistence.history_manager import HistoryManager
from src.core.persistence.extractor import IntelligenceExtractor

load_dotenv()

def test_extraction():
    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )
    chat_id = "test_intelligence_chat"
    
    # 1. Crear un historial simulado con información clave
    history = [
        {"role": "user", "content": "Hola Andrew, soy john.doe."},
        {"role": "assistant", "content": "Hola John, ¿en qué puedo ayudarte hoy?"},
        {"role": "user", "content": "Mira, me gusta mucho la arquería y mi meta para este año es aprender a programar en Rust."},
        {"role": "assistant", "content": "¡Qué bien! La arquería es genial. Y Rust es un lenguaje muy potente."},
        {"role": "user", "content": "Sí, de hecho te recomiendo un restaurante en Cali para comer pizza, se llama 'Pizza Solar', es increíble."}
    ]
    
    HistoryManager.save_history(chat_id, history)
    safe_print(f"✅ Historial simulado guardado en {chat_id}")

    # 2. Ejecutar el extractor
    extractor = IntelligenceExtractor(client)
    extractor.extract_and_persist(chat_id)

    # 3. Verificar resultados en los ledgers
    safe_print("\n🧐 Verificando actualizaciones en ledgers...")
    
    # Verificar Usuario
    user_path = "./assets/users/john.doe.ledger"
    if os.path.exists(user_path):
        with open(user_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            interests = str(data.get("public_profile", {}).get("interests", []))
            goals = str(data.get("private_profile", {}).get("goals", []))
            print(f"  Usuario 'john.doe':")
            print(f"    - Intereses: {interests}")
            print(f"    - Metas: {goals}")
            
            if "arquería" in interests.lower(): safe_print("    ✅ Interés 'arquería' encontrado.")
            if "rust" in goals.lower(): safe_print("    ✅ Meta 'Rust' encontrada.")
    
    # Verificar Ciudad
    city_path = "./assets/cities/cali.ledger"
    if os.path.exists(city_path):
        with open(city_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Manejar estructura con/sin llave raíz
            city_data = data.get("cali", data)
            gastronomia = str(city_data.get("experiencias_gastronomicas", []))
            print(f"  Ciudad 'cali':")
            if "Pizza Solar" in gastronomia:
                safe_print("    ✅ Recomendación 'Pizza Solar' encontrada.")
            else:
                safe_print(f"    ❌ No se encontró 'Pizza Solar'. Contenido actual: {gastronomia[:200]}...")

if __name__ == "__main__":
    test_extraction()
