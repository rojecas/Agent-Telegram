import os
import sys
import json
import time

# Añadir el directorio raíz al path para las importaciones
sys.path.append(os.getcwd())

from src.tools.city_tools import read_city_info
from src.tools.user_tools import read_ledger, list_users

def run_performance_test():
    print("🚀 Iniciando prueba de línea base de rendimiento...")
    
    # 1. Probar lista de usuarios (para obtener un nombre)
    print("\n--- Probando list_users ---")
    users = list_users()
    user_name = users.get("usuarios", ["roman.castaneda"])[0] if users.get("usuarios") else "roman.castaneda"
    
    # 2. Probar read_ledger (Instrumentado)
    print(f"\n--- Probando read_ledger para '{user_name}' ---")
    for i in range(3):
        print(f"  Ejecución {i+1}...")
        read_ledger(user=user_name)
    
    # 3. Probar read_city_info (Instrumentado)
    cities = ["cali", "bogota", "pereira"]
    for city in cities:
        print(f"\n--- Probando read_city_info para '{city}' ---")
        read_city_info(city=city)
    
    print("\n✅ Prueba completada.")
    
    # Verificar si el log se creó
    log_path = "logs/performance.json"
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)
            print(f"\n📊 Se registraron {len(metrics)} métricas en '{log_path}'.")
            # Mostrar la media
            for name in set(m["metric_name"] for m in metrics):
                durations = [m["duration_seconds"] for m in metrics if m["metric_name"] == name]
                avg = sum(durations) / len(durations)
                print(f"  - {name}: promedio {avg:.6f}s ({len(durations)} muestras)")
    else:
        print(f"\n❌ Error: No se encontró el archivo de logs en '{log_path}'.")

if __name__ == "__main__":
    run_performance_test()
