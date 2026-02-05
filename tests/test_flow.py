#!/usr/bin/env python3
"""
Script de prueba para verificar el flujo básico del asistente Andrew Martin.
"""

import sys
import os
sys.path.insert(0, '.')

from dotenv import load_dotenv
from openai import OpenAI
from agents import run_turn

load_dotenv()

client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url=os.getenv("DEEPSEEK_BASE_URL"))

# Simular una conversación simple
messages = [
    {
        "role": "system",
        "content": "Eres Andrew Martin, un asistente IA útil. Responde en español."
    },
    {
        "role": "user",
        "content": "Hola, ¿cómo estás?"
    }
]

print("=== Iniciando prueba de flujo ===")
try:
    run_turn(1, messages, client)
    print("=== Prueba exitosa ===")
except Exception as e:
    print(f"=== Error en prueba: {e}")
    import traceback
    traceback.print_exc()