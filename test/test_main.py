#!/usr/bin/env python3
"""
Prueba de main.py con entrada simulada.
"""
import sys
import os
import io
import contextlib

sys.path.insert(0, '.')

# Redirigir input
def simulate_main():
    from unittest.mock import patch
    
    # Simular entrada de usuario "exit" para salir inmediatamente
    with patch('builtins.input', side_effect=['exit']):
        try:
            # Capturar salida
            with io.StringIO() as buf, contextlib.redirect_stdout(buf):
                import main
                output = buf.getvalue()
                print("=== main.py ejecutado exitosamente ===")
                print("Salida capturada (primeras 500 chars):")
                print(output[:500])
                return True
        except Exception as e:
            print(f"Error al ejecutar main.py: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    simulate_main()