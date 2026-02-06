import time
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
        
        # Log to persistent storage
        performance_logger.log_metric(
            name=func.__name__,
            duration=elapsed,
            metadata={"module": func.__module__}
        )
        
        # Also print to console for immediate visibility
        print(f"⏱️ [PERFORMANCE] {func.__name__} took {elapsed:.6f} seconds")
        
        return result
    return wrapper
