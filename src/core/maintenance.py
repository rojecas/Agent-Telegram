import os
import time
import threading
from datetime import datetime, timedelta
from openai import OpenAI
from src.core.persistence.chat_registry import ChatRegistry
from src.core.persistence.extractor import IntelligenceExtractor
from src.core.persistence.memory_consolidator import MemoryConsolidator

class SessionMaintenanceWorker:
    """Background worker that monitors chat sessions and triggers cleanup on inactivity."""
    
    def __init__(self, client: OpenAI, inactivity_minutes=10, check_interval_seconds=60):
        self.client = client
        self.inactivity_threshold = timedelta(minutes=inactivity_minutes)
        self.check_interval = check_interval_seconds
        self.running = False
        self.thread = None
        self.processed_sessions = set()  # Track already processed sessions
        
    def start(self):
        """Start the background monitoring thread."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        inactivity_min = int(self.inactivity_threshold.total_seconds() / 60)
        print(f"🔄 [MAINTENANCE] Monitor iniciado (inactividad: {inactivity_min} min)")
    
    def stop(self):
        """Stop the background monitoring thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                self._check_inactive_sessions()
            except Exception as e:
                print(f"❌ [MAINTENANCE] Error en monitor: {e}")
            
            time.sleep(self.check_interval)
    
    def _check_inactive_sessions(self):
        """Check all registered chats for inactivity and trigger cleanup."""
        registry = ChatRegistry.get_all()
        now = datetime.now()
        
        for chat_id, info in registry.items():
            # Skip if already processed
            if chat_id in self.processed_sessions:
                continue
            
            # Parse last_seen timestamp
            try:
                last_seen = datetime.fromisoformat(info.get("last_seen", now.isoformat()))
            except:
                continue
            
            # Check if inactive
            inactive_duration = now - last_seen
            if inactive_duration >= self.inactivity_threshold:
                print(f"⏰ [MAINTENANCE] Sesión inactiva detectada: {chat_id} ({inactive_duration.seconds // 60} min)")
                self._process_session(chat_id)
                self.processed_sessions.add(chat_id)
    
    def _process_session(self, chat_id):
        """Run extraction and consolidation for a specific session."""
        try:
            # Intelligence extraction
            extractor = IntelligenceExtractor(self.client)
            extractor.extract_and_persist(chat_id)
            
            # Memory consolidation
            consolidator = MemoryConsolidator(self.client)
            consolidator.consolidate_chat(chat_id)
            
            print(f"✅ [MAINTENANCE] Sesión {chat_id} procesada correctamente.")
        except Exception as e:
            print(f"❌ [MAINTENANCE] Error procesando {chat_id}: {e}")

# Global instance (to be initialized in main.py)
maintenance_worker = None

def start_maintenance_worker(client: OpenAI, inactivity_minutes=10):
    """Initialize and start the maintenance worker."""
    global maintenance_worker
    maintenance_worker = SessionMaintenanceWorker(client, inactivity_minutes)
    maintenance_worker.start()
    return maintenance_worker
