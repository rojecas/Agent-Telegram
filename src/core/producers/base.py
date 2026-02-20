from abc import ABC, abstractmethod
from queue import Queue
from src.core.models import Message

class BaseProducer(ABC):
    """
    Clase base abstracta para todos los productores de mensajes.
    Cada productor corre en su propio hilo y envía objetos Message a una cola central.
    """
    def __init__(self, message_queue: Queue):
        self.message_queue = message_queue
        self.running = False

    @abstractmethod
    def start(self):
        """Inicia el productor."""
        pass

    @abstractmethod
    def stop(self):
        """Detiene el productor de forma segura."""
        pass

    def emit(self, message: Message):
        """Envía un mensaje a la cola central."""
        self.message_queue.put(message)
