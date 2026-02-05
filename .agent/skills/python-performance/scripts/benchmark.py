import time
from functools import wraps

def benchmark(func):
    """
    Decorator to benchmark function execution time.
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
        print(f"⏱️ [PERFORMANCE] {func.__name__} took {elapsed:.6f} seconds")
        return result
    return wrapper

if __name__ == "__main__":
    # Example usage
    @benchmark
    def compute_heavy_task():
        return sum(i**2 for i in range(1000000))
    
    compute_heavy_task()
