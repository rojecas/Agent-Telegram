import time
import os
from functools import wraps
from .performance import performance_logger

def benchmark(func):
    """
    Decorator to benchmark function execution and persist results.
    Usage:
        @benchmark
        def my_function():
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        
        # Log to persistent storage (siempre)
        performance_logger.log_metric(
            name=func.__name__,
            duration=elapsed,
            metadata={"module": func.__module__}
        )
        
        # Solo imprimir en modo development
        if os.getenv("APP_STATUS") == "development":
            print(f"[PERFORMANCE] {func.__name__} took {elapsed:.6f} seconds")
        
        return result
    return wrapper

def debug_print(message: str):
    """
    Print message only in development mode.
    Use this for all debug/tool call prints.
    """
    if os.getenv("APP_STATUS") == "development":
        print(message)
