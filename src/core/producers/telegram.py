import time
import threading
import os
from datetime import datetime
from .base import BaseProducer
from src.core.models import Message
from src.tools.telegram_tool import telegram_receive
from src.core.logger import safe_print

class TelegramProducer(BaseProducer):
    """Productor que realiza polling a la API de Telegram."""
    
    def __init__(self, message_queue):
        super().__init__(message_queue)
        self.thread = None
        self.last_update_id = 0

    def start(self):
        if not os.getenv("TELEGRAM_BOT_TOKEN"):
            safe_print("⚠️ [PRODUCER] TELEGRAM_BOT_TOKEN no encontrado. Productor desactivado.")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        safe_print("✅ [PRODUCER] Telegram iniciado (Polling).")

    def stop(self):
        self.running = False

    def _run(self):
        while self.running:
            try:
                result = telegram_receive(offset=self.last_update_id + 1)
                
                if result.get("success") and result.get("count", 0) > 0:
                    for update in result["updates"]:
                        self.last_update_id = max(self.last_update_id, update["update_id"])
                        
                        msg = Message(
                            priority=2,
                            content=update["text"],
                            source='telegram',
                            user_id=update["chat_id"],
                            chat_id=update["chat_id"],
                            metadata={"username": update["from"]}
                        )
                        self.emit(msg)
                        
                        if os.getenv("APP_STATUS") == "development":
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            print(f"[{timestamp}] Telegram msg de {update['from']} añadido a cola.")
                
                time.sleep(2)
            except Exception as e:
                safe_print(f"❌ Error en productor Telegram: {e}")
                time.sleep(5)
