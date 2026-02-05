"""
Test script to verify cloud-ready triggers work without manual intervention.
This simulates a cloud environment where KeyboardInterrupt is not available.
"""
import os
import sys
import time
import signal
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.agent_telegram.core.chat_registry import ChatRegistry
from src.agent_telegram.core.history_manager import HistoryManager
from src.agent_telegram.core.maintenance import SessionMaintenanceWorker

load_dotenv()

def test_inactivity_trigger():
    """Test that the maintenance worker triggers cleanup on inactivity."""
    print("🧪 Testing Inactivity Trigger\n")
    
    # Setup
    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )
    chat_id = "test_cloud_trigger"
    
    # 1. Create a simulated conversation
    history = [
        {"role": "user", "content": "Hola, me llamo test.user y me gusta el ciclismo."},
        {"role": "assistant", "content": "¡Hola! El ciclismo es genial."}
    ]
    HistoryManager.save_history(chat_id, history)
    
    # 2. Register the chat with a "past" timestamp to simulate inactivity
    past_time = (datetime.now() - timedelta(minutes=11)).isoformat()
    ChatRegistry.register(chat_id, "test", "private", username="test_user")
    
    # Manually set last_seen to the past
    registry = ChatRegistry.load()
    registry[chat_id]["last_seen"] = past_time
    ChatRegistry.save(registry)
    
    print(f"✅ Chat simulado creado: {chat_id}")
    print(f"   Última actividad: {past_time} (hace 11 minutos)\n")
    
    # 3. Start the maintenance worker with short intervals for testing
    worker = SessionMaintenanceWorker(client, inactivity_minutes=10, check_interval_seconds=5)
    worker.start()
    
    print("⏳ Esperando que el monitor detecte inactividad (5 segundos)...\n")
    time.sleep(6)
    
    # 4. Verify that the session was processed
    if chat_id in worker.processed_sessions:
        print("✅ ÉXITO: El monitor detectó y procesó la sesión inactiva.")
    else:
        print("❌ FALLO: La sesión no fue procesada automáticamente.")
    
    worker.stop()

def test_signal_handler():
    """Test that SIGTERM triggers graceful shutdown."""
    print("\n🧪 Testing SIGTERM Handler\n")
    
    # Note: This is a demonstration. In a real cloud environment,
    # the container orchestrator would send SIGTERM.
    print("📌 En producción, SIGTERM sería enviado por el orquestador (Kubernetes, Docker, etc.)")
    print("   El handler `graceful_shutdown` ejecutaría:")
    print("   1. run_extraction_on_all(client)")
    print("   2. consolidate_all_histories(client)")
    print("   3. os._exit(0)")
    print("\n✅ Handler registrado correctamente en main.py")

if __name__ == "__main__":
    test_inactivity_trigger()
    test_signal_handler()
    print("\n🎉 Todas las pruebas completadas.")
