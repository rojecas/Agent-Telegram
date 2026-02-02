"""
Módulo de seguridad refactorizado.

Exporta:
- ThreatDetector (interfaz abstracta)
- PatternThreatDetector (implementación)
- SecurityLogger (interfaz abstracta)
- FileSecurityLogger (implementación)
- security_logger (instancia global de FileSecurityLogger)
"""

from .detector import ThreatDetector, PatternThreatDetector
from .logger import SecurityLogger, FileSecurityLogger

# Instancia global del logger (compatible con el código existente)
security_logger = FileSecurityLogger()

__all__ = [
    "ThreatDetector",
    "PatternThreatDetector",
    "SecurityLogger",
    "FileSecurityLogger",
    "security_logger"
]