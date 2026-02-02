import json
from datetime import datetime
from pathlib import Path

class SecurityLogger:
    """Registra eventos de seguridad del sistema"""
    
    def __init__(self, log_dir="./logs/security"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
    def log_event(self, event_type, details, user=None, threat_level="low"):
        """Registra un evento de seguridad"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "threat_level": threat_level,
            "user": user,
            "details": details,
            "action_taken": "logged"
        }
        
        # Nombre del archivo por fecha
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"security_log_{date_str}.json"
        
        # Cargar logs existentes o crear lista nueva
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # Agregar nuevo log
        logs.append(log_entry)
        
        # Guardar
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
        
        # También imprimir en consola para monitoreo en tiempo real
        print(f"🔒 [SEGURIDAD] {event_type} - Nivel: {threat_level}")
        
        return log_entry
    
    def log_threat_detected(self, threat_type, user_input, response_given, user=None):
        """Registra una amenaza detectada"""
        return self.log_event(
            event_type=f"THREAT_DETECTED_{threat_type.upper()}",
            details={
                "user_input": user_input,
                "response_given": response_given,
                "detection_method": "pattern_matching"
            },
            user=user,
            threat_level="medium"
        )
    
    def log_profile_access(self, user, accessed_by="system", purpose="verification"):
        """Registra acceso a perfil de usuario"""
        return self.log_event(
            event_type="PROFILE_ACCESS",
            details={
                "profile_accessed": user,
                "accessed_by": accessed_by,
                "purpose": purpose,
                "data_protected": True
            },
            user=user,
            threat_level="low"
        )
    
    def log_secret_verification(self, user, success, attempts=1):
        """Registra intento de verificación de secreto"""
        event_type = "SECRET_VERIFICATION_SUCCESS" if success else "SECRET_VERIFICATION_FAILED"
        threat_level = "low" if success else "high"
        
        return self.log_event(
            event_type=event_type,
            details={
                "user": user,
                "success": success,
                "attempts": attempts,
                "timestamp_verified": datetime.now().isoformat() if success else None
            },
            user=user,
            threat_level=threat_level
        )

# Instancia global para uso en todo el sistema
security_logger = SecurityLogger()