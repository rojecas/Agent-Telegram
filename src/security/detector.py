"""
Módulo de detección de amenazas.
Define una interfaz abstracta ThreatDetector y una implementación basada en patrones.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Any, List


class ThreatDetector(ABC):
    """
    Interfaz abstracta para detectores de amenazas de seguridad.
    """
    
    @abstractmethod
    def check_threat(self, user_input: str) -> Optional[Tuple[str, str]]:
        """
        Verifica si el input del usuario contiene una amenaza.
        
        Args:
            user_input: Texto ingresado por el usuario.
            
        Returns:
            Una tupla (threat_type, response) si se detecta una amenaza,
            o None si no hay amenaza.
        """
        pass


class PatternThreatDetector(ThreatDetector):
    """
    Implementación de ThreatDetector que usa patrones de texto configurados.
    """
    
    def __init__(self, patterns: Dict[str, List[str]], responses: Dict[str, str]):
        """
        Inicializa el detector con patrones y respuestas.
        
        Args:
            patterns: Diccionario {threat_type: [list of patterns]}
            responses: Diccionario {threat_type: response_template}
        """
        self.patterns = patterns
        self.responses = responses
    
    @classmethod
    def from_config_dict(cls, config: Dict[str, Any]) -> 'PatternThreatDetector':
        """
        Crea un detector a partir de un diccionario de configuración.
        
        Args:
            config: Debe contener las claves "patterns" y "response_templates"
                   como en SECURITY_CONFIG["threat_detection"].
        
        Returns:
            Instancia de PatternThreatDetector.
        """
        patterns = config.get("patterns", {})
        responses = config.get("response_templates", {})
        return cls(patterns, responses)
    
    def check_threat(self, user_input: str) -> Optional[Tuple[str, str]]:
        """
        Verifica si el input del usuario contiene patrones de amenaza.
        """
        user_input_lower = user_input.lower()
        
        for threat_type, pattern_list in self.patterns.items():
            for pattern in pattern_list:
                if pattern in user_input_lower:
                    response = self.responses.get(threat_type, "Amenaza detectada.")
                    return threat_type, response
        
        return None