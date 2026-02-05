from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Optional, Any

@dataclass(order=True)
class Message:
    "Clase unificada para representar mensajes de diferentes plataformas."
    
    priority: int  # 1: Sistema (Alta), 2: Usuario (Normal)
    content: str = field(compare=False)
    source: Literal['keyboard', 'telegram', 'whatsapp', 'email', 'system'] = field(compare=False)
    user_id: str = field(compare=False)
    chat_id: str = field(compare=False)  # En DMs será igual al user_id
    metadata: dict[str, Any] = field(default_factory=dict, compare=False)
    timestamp: datetime = field(default_factory=datetime.now) # Tie-breaker para PriorityQueue

    def is_group(self) -> bool:
        "Determina si el mensaje viene de un grupo basándose en el chat_id."
        # En Telegram, los IDs de grupos son negativos.
        # En otros sistemas podría ser un prefijo como 'grp_'.
        try:
            return int(self.chat_id) < 0
        except ValueError:
            return self.chat_id.startswith('grp_')
