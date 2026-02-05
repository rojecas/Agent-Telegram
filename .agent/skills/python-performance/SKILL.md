---
name: python-performance
description: Optimization strategies for high-performance Python code, including profiling and concurrency.
---

# Python Performance Optimization Skill

This skill provides patterns and tools to identify and resolve performance bottlenecks in Python applications.

## 1. Core Concepts

- **Profiling:** Always measure before optimizing. Use `cProfile` for CPU and `memory_profiler` for memory.
- **Optimization Strategy:** Focus on "hot paths" (code that runs frequently).
- **Efficient Patterns:** Prefer list comprehensions over loops, and generators for large datasets.

## 2. Best Practices

- **Built-in Functions:** Use them as they are implemented in C.
- **Caching:** Use `functools.lru_cache` for expensive computations.
- **Concurrency:** Use `asyncio` for I/O-bound tasks and `multiprocessing` for CPU-bound tasks.
- **Data Structures:** Use `dict` for fast lookups and `set` for unique membership checks.

## 3. Profiling Tools

- **cProfile:** `python -m cProfile -o output.prof script.py`
- **py-spy:** Sampling profiler for production systems.
- **pytest-benchmark:** Integration for benchmarking tasks during testing.

## 4. Performance Checklist

- [ ] Profiled code to identify bottlenecks.
- [ ] Used appropriate data structures (dict/set).
- [ ] Implemented caching where beneficial.
- [ ] Used generators for large datasets.
- [ ] Benchmarked before and after optimization.
