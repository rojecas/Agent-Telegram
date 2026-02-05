import time
import json
import os
from functools import wraps
from datetime import datetime

# --- Pattern: Persistent Performance Logger ---

class PersistentLogger:
    """Helper to save metrics for long-term analysis."""
    def __init__(self, filename="performance_history.json"):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f: json.dump([], f)

    def record(self, name, duration):
        entry = {
            "at": datetime.now().isoformat(),
            "tool": name,
            "seconds": round(duration, 6)
        }
        with open(self.filename, 'r+') as f:
            data = json.load(f)
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()

logger = PersistentLogger()

def persistent_benchmark(func):
    """Decorator that saves results to a file."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        
        # Persistence
        logger.record(func.__name__, elapsed)
        
        print(f"💾 [SKILL] Metric saved for {func.__name__}: {elapsed:.6f}s")
        return result
    return wrapper

# --- Example Usage ---

@persistent_benchmark
def simulate_tool_execution():
    time.sleep(0.123)
    return "Done"

if __name__ == "__main__":
    print("Running persistent benchmark example...")
    simulate_tool_execution()
    print(f"Check execution metrics in: {os.path.abspath('performance_history.json')}")
