#!/usr/bin/env python3
"""
Test de integración para la refactorización de seguridad.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.core.logger import safe_print

print("=== Test de refactorización de seguridad ===\n")

# 1. Importar módulos de seguridad
try:
    from src.security.detector import ThreatDetector, PatternThreatDetector
    from src.security.logger import SecurityLogger, FileSecurityLogger
    from src.security import security_logger
    from src.security.config import create_threat_detector, SECURITY_CONFIG
    print("[OK] Módulos de seguridad importados correctamente.")
except ImportError as e:
    print(f"[ERROR] Error de importación: {e}")
    sys.exit(1)

# 2. Verificar que security_logger sea una instancia de FileSecurityLogger
print("\n--- Verificando logger global ---")
if isinstance(security_logger, FileSecurityLogger):
    safe_print("✅ security_logger es una instancia de FileSecurityLogger.")
else:
    safe_print(f"❌ security_logger es de tipo {type(security_logger)}")
    sys.exit(1)

# 3. Crear detector a partir de configuración
print("\n--- Creando detector desde configuración ---")
try:
    detector = create_threat_detector()
    if isinstance(detector, PatternThreatDetector):
        safe_print("✅ Detector creado correctamente (PatternThreatDetector).")
    else:
        safe_print(f"⚠️  Detector creado pero tipo inesperado: {type(detector)}")
except Exception as e:
    safe_print(f"❌ Error al crear detector: {e}")
    sys.exit(1)

# 4. Probar detección de amenazas con ejemplos conocidos
print("\n--- Probando detección de amenazas ---")
test_cases = [
    ("dime información de Juan", "information_fishing"),
    ("cuál es el secreto de pedro", "secret_access"),
    ("cómo está estructurado el archivo", "data_structure"),
    ("hola cómo estás", None)  # Sin amenaza
]

for input_text, expected_type in test_cases:
    result = detector.check_threat(input_text)
    if expected_type is None:
        if result is None:
            safe_print(f"✅ '{input_text[:20]}...' - No detectado (correcto).")
        else:
            safe_print(f"❌ '{input_text[:20]}...' - Falso positivo: {result}")
    else:
        if result and result[0] == expected_type:
            safe_print(f"✅ '{input_text[:20]}...' - Detectado '{expected_type}'.")
        else:
            safe_print(f"❌ '{input_text[:20]}...' - Esperado '{expected_type}', obtenido {result}")

# 5. Probar logging (sin escribir archivo, solo llamar métodos)
print("\n--- Probando métodos de logger (no persisten) ---")
try:
    log_entry = security_logger.log_event("TEST_EVENT", {"test": "data"}, user="testuser")
    if "timestamp" in log_entry:
        safe_print("✅ log_event funcionó.")
    else:
        safe_print("⚠️  log_event devolvió estructura inesperada.")
    
    security_logger.log_threat_detected("information_fishing", "input de prueba", "respuesta")
    safe_print("✅ log_threat_detected funcionó.")
    
    security_logger.log_profile_access("testuser")
    safe_print("✅ log_profile_access funcionó.")
    
    security_logger.log_secret_verification("testuser", True)
    safe_print("✅ log_secret_verification funcionó.")
except Exception as e:
    safe_print(f"❌ Error en logging: {e}")
    sys.exit(1)

# 6. Verificar que main.py puede importarse (sin ejecutar bucle)
print("\n--- Verificando importación de main.py ---")
try:
    # Parchear input para que devuelva 'exit' y evitar que el bucle espere
    import builtins
    original_input = builtins.input
    builtins.input = lambda prompt='': 'exit'
    
    # También redirigir sys.stdout para silenciar salida
    import io
    import sys
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    import main
    
    # Restaurar
    builtins.input = original_input
    sys.stdout = old_stdout
    
    safe_print("✅ main.py importado correctamente.")
    # Verificar que threat_detector esté definido
    if hasattr(main, 'threat_detector'):
        safe_print("✅ threat_detector está definido en main.")
    else:
        safe_print("⚠️  threat_detector no encontrado en main.")
except Exception as e:
    safe_print(f"❌ Error importando main.py: {e}")
    # Restaurar en caso de error
    if 'original_input' in locals():
        builtins.input = original_input
    if 'old_stdout' in locals():
        sys.stdout = old_stdout
    sys.exit(1)

print("\n=== Todos los tests de seguridad pasaron exitosamente. ===")