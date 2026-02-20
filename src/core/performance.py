import json
import os
import time
from datetime import datetime
from typing import Dict, Any

class PerformanceLogger:
    def __init__(self, log_file: str = "logs/performance.json"):
        self.log_file = log_file
        self._ensure_log_file()

    def _ensure_log_file(self):
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def log_metric(self, name: str, duration: float, metadata: Dict[str, Any] = None):
        """Logs a performance metric to the JSON file."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "metric_name": name,
            "duration_seconds": round(duration, 6),
            "metadata": metadata or {}
        }
        
        try:
            with open(self.log_file, 'r+', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    data = []
                data.append(entry)
                f.seek(0)
                json.dump(data, f, indent=2)
                f.truncate()
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error logging performance metric: {e}")

# Global instance for shared use
performance_logger = PerformanceLogger()
