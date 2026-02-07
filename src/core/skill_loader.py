import os

def load_skill(skill_name: str) -> str:
    """
    Carga el contenido de una Skill desde el directorio .agent/skills.
    
    Args:
        skill_name (str): Nombre de la skill (nombre del directorio, ej: 'telegram-expert').
        
    Returns:
        str: Contenido del archivo SKILL.md o un string vacío si no se encuentra.
    """
    # Intentar ubicar la raíz del proyecto (donde está .agent)
    # Asumimos que este script corre desde src/agent_telegram/core/ o similar
    # Subimos niveles hasta encontrar .agent o fallar
    
    # Estrategia simple: Usar ruta relativa desde el CWD (que suele ser la raíz al correr main.py)
    skill_path = os.path.join(".agent", "skills", skill_name, "SKILL.md")
    
    if os.path.exists(skill_path):
        try:
            with open(skill_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Opcional: Podríamos parsear el YAML del encabezado, 
                # pero por ahora devolvemos todo el texto crudo para el prompt.
                return content
        except Exception as e:
            print(f"⚠️ Error cargando Skill '{skill_name}': {e}")
            return ""
    else:
        print(f"⚠️ Skill no encontrada: {skill_path}")
        return ""
