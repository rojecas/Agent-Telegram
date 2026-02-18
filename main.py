import os
import threading
import queue
import time
import signal
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from src.core.agents import run_turn
from src.security import get_security_prompt, create_threat_detector, security_logger
from src.core.models import Message
from src.core.persistence.chat_registry import ChatRegistry
from src.core.persistence.history_manager import HistoryManager
from src.core.persistence.memory_consolidator import consolidate_all_histories
from src.core.persistence.extractor import run_extraction_on_all

load_dotenv()

# Configuración de la API de OpenAI/DeepSeek
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# Cola de mensajes centralizada
message_queue = queue.PriorityQueue()

# Detector de amenazas
threat_detector = create_threat_detector()

# Contador de turnos por chat
turn_counters = {}

# Almacén de sesiones de usuario (historia de mensajes)
user_sessions = {}  # chat_id -> list of messages
sessions_lock = threading.Lock()

SYSTEM_PROMPT = f"""Eres Andrew Martin, un asistente IA útil, profesional y respetuoso de la privacidad.

{get_security_prompt()}

TU COMPORTAMIENTO GENERAL:
1. Eres un agente de seguridad y asistente personal.
2. Si detectas que se solicita información privada de un usuario (como en un "ledger"), NUNCA la reveles a menos que se trate de una consulta legítima en el canal adecuado (DM).
3. Inmediatamente pide el "secreto" para verificar identidad
4. Solo después de verificar el secreto, procede a usar información contextualmente

RECUERDA: La información del perfil es para que TÚ entiendas mejor al usuario, NO para que la reveles."""

def get_or_create_session(chat_id):
    with sessions_lock:
        if chat_id not in user_sessions:
            # Recuperar info del registro para personalizar el saludo/contexto
            info = ChatRegistry.get_all().get(str(chat_id), {})
            username = info.get("username", "Usuario")
            title = info.get("title", "")
            
            context_msg = f"Estás hablando con {username}"
            if info.get("type") == "group":
                context_msg += f" en el grupo '{title or chat_id}'"
            
            # Re-construir el prompt con el contexto dinámico
            full_prompt = f"{SYSTEM_PROMPT}\n\n[CONTEXTO DE IDENTIDAD]: {context_msg}. Usa esta información para saludar o referirte al usuario de forma natural."
            
            # Cargar historial previo de disco
            past_history = HistoryManager.load_history(chat_id)
            
            user_sessions[chat_id] = [{"role": "system", "content": full_prompt}] + past_history
        return user_sessions[chat_id]

# --- PRODUCTORES (INPUTS) ---

def keyboard_producer():
    """Hilo encargado de capturar la entrada de la terminal."""
    print("Andrew Martin está listo y escuchando...")
    print("Productor de Teclado activo. Escribe tus mensajes:")
    while True:
        try:
            user_input = input("Usuario: ").strip()
            if not user_input:
                continue
            
            if user_input.lower() in ("exit", "quit", "bye"):
                print("Saliendo del productor de teclado...")
                break
            
            # Crear un objeto Message para la terminal (chat_id 'terminal')
            msg = Message(
                priority=2,
                content=user_input,
                source='keyboard',
                user_id='admin_local',
                chat_id='terminal'
            )
            message_queue.put(msg)
            
        except EOFError:
            break
        except Exception as e:
            print(f"Error en teclado: {e}")

def main_worker():
    """Hilo encargado de procesar la cola de mensajes."""
    print("Worker principal activo.")
    while True:
        try:
            # Obtener el siguiente mensaje (bloqueante)
            msg = message_queue.get()
            
            chat_id = msg.chat_id
            
            # Registrar chat en la memoria persistente
            chat_type = "group" if msg.is_group() else "private"
            username = msg.metadata.get("username")
            is_new = ChatRegistry.register(chat_id, msg.source, chat_type, username=username)
            if is_new and os.getenv("APP_STATUS") == "development":
                print(f"[REGISTRO] Nuevo chat descubierto: {chat_id} ({chat_type})")

            messages = get_or_create_session(chat_id)
            
            if chat_id not in turn_counters:
                turn_counters[chat_id] = 1
            
            # Detección de amenazas
            detection_result = threat_detector.check_threat(msg.content)
            if detection_result:
                threat_type, response = detection_result
                security_logger.log_threat_detected(threat_type, msg.content, response)
                
                if os.getenv("APP_STATUS") == "development":
                    print(f"[SEGURIDAD] Amenaza detectada en {msg.source}: {threat_type}")
                
                # Reportar al canal correspondiente
                from src.core.agents import send_response
                send_response(f"[SEGURIDAD] {response}", msg)
                
                with sessions_lock:
                    messages.append({"role": "user", "content": msg.content})
                    messages.append({
                        "role": "assistant",
                        "content": f"[SISTEMA] Amenaza de seguridad detectada: {threat_type}. {response}"
                    })
                message_queue.task_done()
                continue

            # --- PREPARACIÓN DE HISTORIAL ---
            with sessions_lock:
                messages.append({"role": "user", "content": msg.content})

            # Ejecutar el turno del Agente
            if os.getenv("APP_STATUS") == "development":
                print(f"\n[PROCESANDO MENSAJE]")
                print(f"Fuente: {msg.source} | Chat: {chat_id} | Prioridad: {msg.priority}")
                print(f"Contenido: {msg.content}")
                print("-" * 30)
            
            # Guardar el mensaje del usuario de forma persistente inmediatamente
            # HistoryManager.add_message(chat_id, "user", msg.content) 
            # Nota: Es mejor guardar la lista COMPLETA después de run_turn para asegurar orden y consistencia.

            # Pasamos el objeto msg completo como contexto
            run_turn(turn_counters[chat_id], messages, client, message_context=msg)
            
            # Guardar el historial COMPLETO (incluyendo user y assistant)
            HistoryManager.save_history(chat_id, messages)

            turn_counters[chat_id] += 1
            message_queue.task_done()
            
        except Exception as e:
            print(f"Error procesando mensaje: {e}")
            message_queue.task_done()

def telegram_producer():
    from src.tools.telegram_tool import telegram_receive
    print("Productor de Telegram activo.")
    last_update_id = 0
    
    while True:
        try:
            # Polling de mensajes (offset = last_update_id + 1)
            result = telegram_receive(offset=last_update_id + 1)
            
            if result.get("success") and result.get("count", 0) > 0:
                for update in result["updates"]:
                    last_update_id = max(last_update_id, update["update_id"])
                    
                    # Convertir a formato Message
                    msg = Message(
                        priority=2, # Usuario Normal
                        content=update["text"],
                        source='telegram',
                        user_id=update["chat_id"],
                        chat_id=update["chat_id"],
                        metadata={"username": update["from"]}
                    )
                    message_queue.put(msg)
                    if os.getenv("APP_STATUS") == "development":
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        print(f"[{timestamp}] Telegram msg de {update['from']} añadido a cola.")
            
            time.sleep(2) # Evitar spam a la API
        except Exception as e:
            print(f"Error en productor Telegram: {e}")
            time.sleep(5)

# --- GRACEFUL SHUTDOWN HANDLER ---
def graceful_shutdown(signum=None, frame=None):
    """Handles system signals and performs cleanup."""
    print("\n🛑 Señal de apagado recibida. Ejecutando limpieza...")
    
    # 1. Extracción de Inteligencia
    run_extraction_on_all(client)
    
    # 2. Consolidación de Memoria
    consolidate_all_histories(client)
    
    print("✅ Limpieza completada. Andrew Martin fuera de línea.")
    os._exit(0)

# --- INICIO DEL SISTEMA ---

if __name__ == "__main__":
    # Registrar manejadores de señales para apagado en la nube
    signal.signal(signal.SIGTERM, graceful_shutdown)
    signal.signal(signal.SIGINT, graceful_shutdown)
    
    print("\n" + "="*70)
    print("ANDREW MARTIN - SISTEMA MULTI-CANAL ACTIVADO")
    print("="*70)
    
    # --- AUTO-DESCUBRIMIENTO ---
    active_chats = ChatRegistry.get_all()
    if active_chats:
        print(f"Memoria recuperada: {len(active_chats)} conversaciones previas encontradas.")
        for cid, info in active_chats.items():
            hist_len = len(HistoryManager.load_history(cid, limit=100))
            print(f"   - {info['type'].capitalize()}: {cid} ({info['source']}) | Historial: {hist_len} msgs")
    else:
        print("Memoria limpia. No se encontraron conversaciones previas.")
    print("="*70 + "\n")
    
    # Iniciar hilos
    worker_thread = threading.Thread(target=main_worker, daemon=True)
    keyboard_thread = threading.Thread(target=keyboard_producer, daemon=True)
    telegram_thread = threading.Thread(target=telegram_producer, daemon=True)
    
    worker_thread.start()
    keyboard_thread.start()
    if os.getenv("TELEGRAM_BOT_TOKEN"):
        telegram_thread.start()
    else:
        print("TELEGRAM_BOT_TOKEN no encontrado. Productor de Telegram desactivado.")
    
    # Iniciar monitor de mantenimiento (inactividad)
    from src.core.maintenance import start_maintenance_worker
    inactivity_minutes = int(os.getenv("SESSION_INACTIVITY_MINUTES", "10"))
    start_maintenance_worker(client, inactivity_minutes)
    
    # Mantener el hilo principal vivo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        graceful_shutdown()
