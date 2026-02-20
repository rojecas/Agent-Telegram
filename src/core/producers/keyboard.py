import threading
from .base import BaseProducer
from src.core.models import Message
from src.core.logger import safe_print

class KeyboardProducer(BaseProducer):
    """Productor que captura la entrada de la terminal."""
    
    def __init__(self, message_queue):
        super().__init__(message_queue)
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        safe_print("✅ [PRODUCER] Teclado iniciado.")

    def stop(self):
        self.running = False

    def _run(self):
        print("Andrew Martin está listo y escuchando...")
        print("Productor de Teclado activo. Escribe tus mensajes:")
        while self.running:
            try:
                user_input = input("Usuario: ").strip()
                if not user_input:
                    continue
                
                if user_input.lower() in ("exit", "quit", "bye"):
                    print("Saliendo del productor de teclado...")
                    self.running = False
                    break
                
                msg = Message(
                    priority=2,
                    content=user_input,
                    source='keyboard',
                    user_id='admin_local',
                    chat_id='terminal'
                )
                self.emit(msg)
                
            except EOFError:
                break
            except Exception as e:
                safe_print(f"❌ Error en productor teclado: {e}")
