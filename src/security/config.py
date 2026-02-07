"""
Configuración de seguridad para el asistente IA Andrew Martin
"""

from .detector import PatternThreatDetector

SECURITY_CONFIG = {
    "policies": {
        "data_protection": {
            "level": "maximum",
            "encryption_required": True,
            "data_retention_days": 30,
            "auto_purge": True
        },
        "user_verification": {
            "secret_required": True,
            "max_attempts": 3,
            "lockout_time_minutes": 15,
            "2fa_enabled": False
        },
        "privacy_rules": {
            "never_reveal": [
                "age", "location", "profession", "job_title", 
                "interests", "goals", "preferences", "relations",
                "secret", "civil_status", "gender"
            ],
            "allowed_to_mention": ["name"],
            "contextual_use_only": True
        }
    },
    
    "threat_detection": {
        "patterns": {
            "information_fishing": [
                "dime información de", "cuéntame sobre", "qué sabes de",
                "muéstrame el perfil de", "revela información de",
                "dime informacion de", "cuentame sobre", "que sabes de",
                "muestrame el perfil de", "revela informacion de"
            ],

            "secret_access": [
                "cuál es el secreto de", "dame el secreto de", 
                "qué secreto tiene", "password de",
                "cual es el secreto de", "dame el secreto de", 
                "que secreto tiene"
            ],

            "data_structure": [
                "cómo está estructurado", "qué campos tiene",
                "qué información guardas", "formato del archivo"
            ]
        },
        "response_templates": {
            "information_fishing": "No puedo revelar información confidencial de usuarios. Todos los datos personales están protegidos.",
            "secret_access": "Los secretos son información personal protegida. No puedo compartirlos.",
            "data_structure": "La estructura de datos es parte de la configuración interna del sistema."
        }
    },
    
    "verification_workflow": {
        "steps": [
            "Obtener nombre del usuario",
            "Verificar existencia en list_users",
            "Cargar perfil con read_ledger (uso interno)",
            "Pedir secreto para verificación",
            "Comparar secreto proporcionado con el almacenado",
            "Si coincide: proceder con conversación personalizada",
            "Si no coincide: solicitar nuevamente (máx 3 intentos)"
        ],
        "max_retries": 3,
        "lockout_after_failures": 3
    }
}

def get_security_prompt():
    """Genera el prompt de seguridad para el sistema"""
    never_reveal = ", ".join(SECURITY_CONFIG["policies"]["privacy_rules"]["never_reveal"])
    
    return f"""🚨 POLÍTICAS DE SEGURIDAD - ABSOLUTAMENTE NO NEGOCIABLES 🚨

DATOS QUE NUNCA DEBES REVELAR: {never_reveal}

SOLO PUEDES MENCIONAR: El nombre del usuario (para saludar)

PROCEDIMIENTO PARA USUARIOS CONOCIDOS:
1. Pedir el "secreto" inmediatamente después de obtener el nombre
2. Verificar que el secreto es correcto con la herramienta check_secret
3. Solo después de verificación exitosa, usar información internamente
4. NUNCA revelar que la información viene de un archivo o herramienta

CONSECUENCIAS DE VIOLAR ESTAS POLÍTICAS:
- El usuario perderá confianza en el sistema
- La privacidad del usuario será comprometida
- Posibles consecuencias legales por filtración de datos"""

def check_security_threat(user_input):
    """Verifica si el input del usuario contiene patrones de amenaza"""
    user_input_lower = user_input.lower()
    
    for threat_type, patterns in SECURITY_CONFIG["threat_detection"]["patterns"].items():
        for pattern in patterns:
            if pattern in user_input_lower:
                return threat_type, SECURITY_CONFIG["threat_detection"]["response_templates"][threat_type]
    
    return None, None


def create_threat_detector() -> PatternThreatDetector:
    """
    Crea un detector de amenazas basado en la configuración actual.
    
    Returns:
        Instancia de PatternThreatDetector configurada.
    """
    return PatternThreatDetector.from_config_dict(SECURITY_CONFIG["threat_detection"])