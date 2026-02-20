# AGENTS.md - Guía para Agentes de Desarrollo

## 📋 Introducción al Proyecto

**Andrew Martin** es un asistente IA multi-canal con arquitectura SOLID, seguridad avanzada y sistema de memoria persistente.
El proyecto utiliza:
- **Cola prioritaria** (`PriorityQueue`) para el procesamiento multi-canal (Telegram, WhatsApp, etc.) de las interacciones con los usuarios.
- **Privacy Firewall** con detección de amenazas configurables (como intentos de phishing, malware, etc.)
- **Sistema de herramientas para el agente (tool_list)** dinámico con registro automático de las mismas. permitiendo agregar nuevas herramientas de forma sencilla, sin modificar el código del agente.
- **Memoria persistente** en `assets/` con formato `.ledger`

---

## 🚀 Quick Start para Agentes

### 1. Agregar una Nueva Herramienta
```python
# 1. Crear schema en archivo de tools existente (ej: src/tools/misc_tools.py)
MY_TOOL_SCHEMA = {
    "description": "Descripción clara de lo que hace la herramienta",
    "parameters": {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Descripción del parámetro"}
        },
        "required": ["param1"]
    }
}

# 2. Implementar función con decorador @tool
@tool(schema=MY_TOOL_SCHEMA)
def my_tool(param1: str, **kwargs) -> Dict[str, Any]:
    """Implementación con type hints y manejo de errores."""
    try:
        # Lógica de la herramienta
        return {"success": True, "result": "valor"}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}

# 3. Registrar el archivo de la herramienta en el mapeo de `SKILL_MAP` dentro de `src/core/skill_manager.py`
# El decorador @tool registrará la herramienta únicamente cuando el Skill asociado sea activado por el LLM.
```

### 2. Modificar el Sistema de Seguridad
```python
# 1. Editar patrones en src/security/config.py:32-52
SECURITY_CONFIG["threat_detection"]["patterns"]["nuevo_tipo"] = [
    "patrón 1",
    "patrón 2"
]

# 2. Agregar respuesta en :53-57
SECURITY_CONFIG["threat_detection"]["response_templates"]["nuevo_tipo"] = "Mensaje de respuesta"

# 3. El detector se recrea automáticamente al iniciar (main.py:29)
```

### 3. Extender el Sistema de Memoria
```python
# 1. Para nuevos tipos de datos, crear directorio en assets/
# assets/nuevo_tipo/ con archivos .ledger

# 2. Usar patrones existentes de src/tools/user_tools.py:
# - Sanitización de nombres (líneas 51-83)
# - Manejo de homónimos (juan.perez.ledger -> juan.perez.1.ledger)
# - JSON con indent=2, ensure_ascii=False
```

### 4. Integrar Skills Existentes
```python
# 1. Skills disponibles en .agent/skills/:
# - telegram-expert, python-performance, architecture-manager
# - coding-standards, git-expert, karpathy-guidelines
# - semantic-versioning, software-architecture, solid

# 2. Cargador existente: src/core/skill_loader.load_skill()
# 3. Para integrar: modificar SYSTEM_PROMPT en main.py:38-48
# 4. Crear herramienta use_skill() que llame a load_skill()
```

---

## 🛠️ Comandos de Build y Test

### Ejecutar Tests
```bash
# Todos los tests
python -m pytest tests/

# Test individual
python tests/unit/test_tools_refactor.py

# Test de integración específico
python tests/integration/test_intelligence_extraction.py

# Modo desarrollo para debug output
export APP_STATUS=development  # Linux/Mac
set APP_STATUS=development     # Windows CMD
$env:APP_STATUS="development"  # PowerShell
```

### Notas Importantes
- **No hay linting formal** configurado (black, ruff, etc.)
- **No hay type checking** configurado (mypy, pyright)
- **No hay pre-commit hooks** detectados
- **Tests usan unittest.TestCase** como base

---

## 📝 Guías de Estilo de Código

### Importaciones y Estructura
```python
# 1. Standard library imports
import os
import json
from datetime import datetime

# 2. Third-party imports
from openai import OpenAI
from dotenv import load_dotenv

# 3. Local imports (absolutas desde src/)
from src.tools.registry import tool_registry
from src.core.models import Message

# 4. Integración del orquestador de herramientas
from src.core.skill_manager import skill_manager # Carga herramientas bajo demanda
```

### Tipos y Nombrado
```python
# snake_case para funciones/variables
def add_user(name: str, lastname: str) -> Dict[str, Any]:
    user_data = {"name": name, "lastname": lastname}

# CamelCase para clases
class HistoryManager:
    def save_history(self, chat_id: str, messages: List[Dict]) -> bool:

# UPPER_CASE para constantes
MAX_HISTORY_LENGTH = 100
TELEGRAM_API_BASE = "https://api.telegram.org/bot"

# Type hints obligatorios en funciones públicas
def process_message(msg: Message) -> Optional[str]:
```

### Registro de Herramientas (Patrón Clave)
```python
# Ejemplo completo de src/tools/user_tools.py
ADD_USER_SCHEMA = {
    "description": "Crea nuevo usuario con perfil público/privado",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Nombre"},
            "lastname": {"type": "string", "description": "Apellido"},
            "secret": {"type": "string", "description": "Secreto privado"}
        },
        "required": ["name", "lastname", "secret"]
    }
}

@tool(schema=ADD_USER_SCHEMA)
def add_user(name: str, lastname: str, secret: str, **kwargs) -> Dict[str, Any]:
    """Documentación de la función aquí."""
    # Implementación...
```

### Sanitización de Nombres de Archivo
```python
# Patrón específico de user_tools.py:51-83 para homónimos
# juan.perez.ledger -> juan.perez.1.ledger -> juan.perez.2.ledger

base_filename = f"{first_name}.{last_name}"  # juan.perez
filename = f"{base_filename}.ledger"
counter = 0

while os.path.exists(os.path.join(users_dir, filename)):
    counter += 1
    filename = f"{base_filename}.{counter}.ledger"
```

### Manejo de Errores
```python
# Siempre retornar dict con estructura consistente
try:
    # Operación que puede fallar
    result = perform_operation()
    return {"success": True, "data": result, "message": "Éxito"}
except SpecificException as e:
    return {"error": f"Error específico: {str(e)}"}
except Exception as e:
    return {"error": f"Error inesperado: {str(e)}"}
```

### Thread Safety
```python
# Usar threading.Lock para recursos compartidos (main.py:34-36)
sessions_lock = threading.Lock()

def get_or_create_session(chat_id):
    with sessions_lock:  # Context manager para seguridad
        if chat_id not in user_sessions:
            user_sessions[chat_id] = []
        return user_sessions[chat_id]
```

### Persistencia de Archivos
```python
# Guardar en assets/ con extensión .ledger
file_path = os.path.join("assets", "users", f"{username}.ledger")
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)  # indent=2, ASCII false para UTF-8
```

---

## 🔐 Consideraciones de Seguridad

### Variables de Entorno
```bash
# REQUERIDO en .env (no committear!)
DEEPSEEK_API_KEY=tu_clave_aquí
DEEPSEEK_BASE_URL=https://api.deepseek.com

# OPCIONAL para Telegram
TELEGRAM_BOT_TOKEN=token_de_bot
TELEGRAM_CHAT_ID=id_de_chat
```

### Reglas de Privacidad
1. **NUNCA** revelar información de `private_profile` en grupos
2. **SIEMPRE** verificar secreto con `check_secret` antes de acceder datos privados
3. **USAR** `Privacy Firewall` para detectar solicitudes sospechosas
4. **LOGEAR** amenazas en `logs/security/` para auditoría

### Archivos que NUNCA Committear
- `.env` o cualquier archivo con credenciales
- `assets/users/*.ledger` (datos de usuarios reales en producción)
- `logs/` (pueden contener información sensible)

---

## 🧪 Testing Guidelines

### Estructura de Tests
```
tests/
├── unit/           # Tests unitarios
│   ├── test_tools_refactor.py      # Verifica registro de tools
│   ├── test_security_refactor.py   # Pruebas de seguridad
│   └── test_concurrency.py         # Validación de cola prioritaria
└── integration/    # Tests de integración
    ├── test_intelligence_extraction.py
    ├── test_cloud_triggers.py
    └── verify_performance.py
```

### Patrón de Importación en Tests
```python
# tests/unit/test_tools_refactor.py:6-10
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Luego importar desde src/
from src.tools.registry import tool_registry
```

---

## 🏗️ Arquitectura Clave

### Sistema de Cola Prioritaria
```python
# main.py:26-27 - Cola central
message_queue = queue.PriorityQueue()

# src/core/models.py:5-16 - Message con ordenamiento
@dataclass(order=True)
class Message:
    priority: int  # 1: Alta (Sistema), 2: Normal (Usuario)
    content: str = field(compare=False)
    timestamp: datetime = field(default_factory=datetime.now)  # Tie-breaker
```

### Flujo de Datos
1. **Producers** (keyboard_producer, telegram_producer) → `Message` objects
2. **Priority Queue** → ordena por `priority`, luego `timestamp`
3. **Main Worker** → procesa mensajes, aplica seguridad, ejecuta tools
4. **Output Router** → envía respuestas al canal correspondiente

---

## 🔧 Configuración Faltante

### Herramientas No Configuradas
- **Linter**: No hay black, ruff, o flake8 configurado
- **Type Checker**: No hay mypy o pyright configurado
- **Pre-commit**: No hay hooks de git pre-commit
- **Formateo**: No hay .editorconfig o configuración de IDE

### Skills No Integradas
- **Cargador**: `src/core/skill_loader.py` existe pero no se usa
- **Skills**: 10 skills en `.agent/skills/` disponibles
- **Integración**: Requiere modificar `SYSTEM_PROMPT` y crear herramienta `use_skill`

---

## 📞 Referencias Rápidas

### Archivos Clave
- `main.py` - Punto de entrada, orquestación multi-hilo
- `src/core/agents.py` - Lógica del agente, registro de tools
- `src/core/models.py` - Clase Message, definiciones de datos
- `src/tools/registry.py` - Sistema de registro de herramientas
- `src/security/config.py` - Configuración de políticas

### Variables de Entorno Clave
- `APP_STATUS=development` - Habilita debug output
- `SESSION_INACTIVITY_MINUTES=10` - Tiempo para mantenimiento automático
- `DEEPSEEK_API_KEY` - REQUERIDO para API de DeepSeek

### ⚠️ IMPORTANTE: Entornos Virtuales vs .env
**Confusión común**: `.env` (variables) ≠ `.venv` (entorno Python)

| Concepto | Propósito | Ubicación | Cómo usar |
|----------|-----------|-----------|-----------|
| **`.env`** | Variables de configuración | Archivo `.env` en raíz | Cargado automáticamente por `python-dotenv` |
| **`.venv/`** | Entorno virtual Python | Directorio `.venv/` en raíz | Activar: `.venv\Scripts\activate` (Windows) |

**Problema típico**: Ejecutar con Python global (`C:\Python312\python.exe`) en lugar de Python del entorno virtual.

**Solución**:
```bash
# 1. Activar entorno virtual
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# 2. Verificar Python correcto
python -c "import sys; print(sys.executable)"
# Debe mostrar: .venv\Scripts\python.exe

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
python main.py
```

### Dependencias Específicas por Módulo
- **`web_tools.py`**: `ddgs` (o `duckduckgo-search`) + `beautifulsoup4` + `requests`
- **`telegram_tool.py`**: `requests` (API de Telegram)
- **Herramientas locales**: Solo dependencias estándar de Python

**NOTA**: Si las herramientas web fallan con `"ddgs no está instalada"`, verifica que el entorno virtual esté activado y las dependencias instaladas.

### Comandos Útiles
```bash
# Iniciar Andrew Martin
python main.py

# Verificar imports y registro de tools
python tests/unit/test_tools_refactor.py

# Verificar seguridad
python tests/unit/test_security_refactor.py

# Ejecutar todos los tests
python -m pytest tests/ -v
```

### 🔧 Solución de Problemas Comunes

#### Problema 1: "ddgs no está instalada" o "beautifulsoup4 no está instalada"
**Síntoma**: Herramientas `web_search`/`read_url` fallan con error de dependencia.
**Causa**: Entorno virtual no activado o dependencias no instaladas.
**Solución**:
```bash
# 1. Verificar entorno virtual activado
python -c "import sys; print(sys.executable)"
# Si muestra C:\Python312\python.exe → entorno NO activado

# 2. Activar entorno virtual
.venv\Scripts\activate

# 3. Instalar dependencias faltantes
pip install ddgs beautifulsoup4
# o reinstalar todas:
pip install -r requirements.txt
```

#### Problema 2: "ModuleNotFoundError" en imports
**Síntoma**: Error al importar módulos de `src/`.
**Causa**: PYTHONPATH incorrecto o ejecución desde directorio equivocado.
**Solución**:
```bash
# Ejecutar siempre desde la raíz del proyecto
cd D:\MySource\IA\Agent-Telegram
python main.py
```

#### Problema 3: Tests pasan pero herramientas no funcionan
**Síntoma**: Tests unitarios OK, pero `web_search` retorna error.
**Causa**: Tests usan mocks, pero herramientas reales necesitan dependencias.
**Solución**: Instalar dependencias de producción (ver Problema 1).

#### Problema 4: UnicodeEncodeError con emojis
**Síntoma**: Error `'charmap' codec can't encode character` en Windows.
**Causa**: Consola Windows no soporta UTF-8 por defecto.
**Solución**:
```bash
# Opción 1: Usar PowerShell o Terminal Windows (recomendado)
# Opción 2: Configurar consola: chcp 65001
# Opción 3: Ejecutar sin emojis: set APP_STATUS=production
```

---

**Última actualización**: 2026-02-06
**Basado en análisis de**: README.md, main.py, src/, tests/, .agent/skills/
