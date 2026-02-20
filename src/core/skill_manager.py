
import importlib
import sys
from typing import Dict, List, Optional
from src.tools.registry import tool, tool_registry
from src.core.logger import safe_print

# Mapeo de Skills a módulos de herramientas
SKILL_MAP: Dict[str, List[str]] = {
    "social": [
        "src.tools.telegram_tool",
        "src.tools.user_tools",
        "src.tools.group_tools"
    ],
    "web": [
        "src.tools.web_tools"
    ],
    "utility": [
        "src.tools.datetime_tool",
        "src.tools.city_tools",
        "src.tools.misc_tools"
    ],
    "system": [
        "src.tools.system_tools"
    ]
}

class SkillManager:
    """Gestiona la carga dinámica de grupos de herramientas (Skills)."""
    
    def __init__(self):
        self.active_skills: List[str] = []
        self.loaded_modules: List[str] = []

    def activate_skill(self, skill_name: str) -> bool:
        """Carga los módulos asociados a un skill si no están ya cargados."""
        if skill_name not in SKILL_MAP:
            safe_print(f"⚠️ Skill desconocido: {skill_name}")
            return False
        
        if skill_name in self.active_skills:
            return True
        
        safe_print(f"🧠 Activando skill: {skill_name}...")
        
        success = True
        for module_path in SKILL_MAP[skill_name]:
            if module_path not in self.loaded_modules:
                try:
                    # Carga dinámica del módulo para que se ejecuten los decoradores @tool
                    importlib.import_module(module_path)
                    self.loaded_modules.append(module_path)
                    safe_print(f"  ✅ Módulo cargado: {module_path}")
                except Exception as e:
                    safe_print(f"  ❌ Error cargando {module_path}: {e}")
                    success = False
        
        if success:
            self.active_skills.append(skill_name)
            return True
        return False

# Instancia global del SkillManager
skill_manager = SkillManager()

# Registro de la herramienta maestra
@tool({
    "description": "Activa un grupo de herramientas (Skill) específico para que el agente pueda usarlas. Usa esto cuando necesites realizar tareas que requieren herramientas no disponibles actualmente (ej: búsquedas web, gestión de telegram, utilidades).",
    "parameters": {
        "type": "object",
        "properties": {
            "skill_name": {
                "type": "string",
                "enum": list(SKILL_MAP.keys()),
                "description": "El nombre del skill a activar."
            }
        },
        "required": ["skill_name"]
    }
})
def request_skill_activation(skill_name: str) -> str:
    """Herramienta llamada por el LLM para activar capacidades extra."""
    if skill_manager.activate_skill(skill_name):
        return f"Skill '{skill_name}' activado con éxito. Ahora tienes nuevas herramientas disponibles."
    else:
        return f"Error al intentar activar el skill '{skill_name}'. Revisa el nombre del skill."
