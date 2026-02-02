# Andrew Martin – Asistente IA con Seguridad Avanzada

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI%20API-1.12%2B-green)](https://platform.openai.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![SOLID](https://img.shields.io/badge/Design-SOLID%20Principles-orange)](https://en.wikipedia.org/wiki/SOLID)

**Andrew Martin** es un asistente conversacional inteligente desarrollado como prueba de concepto, que combina capacidades de IA con un sistema de seguridad robusto y una arquitectura modular diseñada bajo los principios SOLID.

El asistente puede interactuar con usuarios mediante un chat en terminal, verificar identidades, gestionar perfiles personales, detectar amenazas de seguridad y ejecutar herramientas especializadas (consultar información de ciudades, obtener la hora, editar archivos, etc.) utilizando el modelo de lenguaje DeepSeek.

---

## 🚀 Características principales

- **🤖 Conversación contextual** – Usa el modelo DeepSeek con capacidad de razonamiento (`reasoning_content`) para respuestas más precisas y naturales.
- **🔐 Sistema de seguridad de tres capas**
  1. **Verificación de identidad** – Los usuarios deben proporcionar un secreto personal para acceder a su perfil.
  2. **Detección de amenazas** – Patrones configurables que identifican intentos de fishing, acceso a secretos o preguntas sobre estructura de datos.
  3. **Logging de auditoría** – Todos los eventos de seguridad se registran en archivos JSON con timestamp y nivel de amenaza.
- **🧰 Herramientas modulares** – Doce herramientas organizadas por dominio (usuarios, ciudades, fecha/hora, misceláneas, Telegram) registradas dinámicamente mediante decoradores.
- **📁 Persistencia de datos** – Perfiles de usuarios y datos de ciudades almacenados en archivos `.ledger` (JSON seguro) dentro de `assets/`.
- **🧪 Suite de pruebas** – Tests unitarios y de integración que validan la refactorización y el cumplimiento de SOLID.
- **⚙️ Configuración centralizada** – Parámetros de seguridad, prompts del sistema y patrones de detección en `security_config.py`.

---

## 🏗️ Arquitectura del sistema

### Visión general
El proyecto sigue una arquitectura por capas con separación clara de responsabilidades:

```
┌─────────────────────────────────────────────────────────┐
│                    Capa de Presentación                  │
│  (main.py) – Interfaz de línea de comandos, bucle       │
│  principal, detección de amenazas, gestión de flujo.    │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────┐
│                    Capa de Agente                        │
│  (agents.py) – Orquestación de turnos, llamadas a       │
│  herramientas, manejo del historial de conversación.    │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────┐
│               Capa de Servicios / Herramientas          │
│  (tools/) – Funcionalidades específicas agrupadas por   │
│  dominio, registradas en un ToolRegistry central.       │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────┐
│               Capa de Seguridad                         │
│  (security/) – Interfaces abstractas (ThreatDetector,   │
│  SecurityLogger) e implementaciones concretas.          │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────┐
│               Capa de Datos / Configuración             │
│  (assets/, security_config.py) – Almacenamiento         │
│  persistente y configuración de reglas.                 │
└─────────────────────────────────────────────────────────┘
```

### Componentes clave

#### 1. **Módulo de herramientas (`tools/`)**
- **`ToolRegistry`** – Patrón de registro central que mantiene un mapa de nombre‑función‑esquema.
- **Decorador `@tool`** – Permite registrar funciones automáticamente sin modificar listas manuales.
- **Organización por dominio**:
  - `user_tools.py`: gestión de perfiles (`add_user`, `list_users`, `read_ledger`).
  - `city_tools.py`: información de ciudades (`read_city_info`, `add_city_info`).
  - `datetime_tool.py`: obtención de hora/fecha en diferentes zonas.
  - `misc_tools.py`: utilidades generales (`get_weather`, `edit_file`).
  - `telegram_tool.py`: comunicación con Telegram (`telegram_send`, `telegram_receive`, `telegram_set_webhook`, `telegram_get_me`).

*Beneficios arquitectónicos*: **SRP** (cada módulo tiene una única responsabilidad), **OCP** (nuevas herramientas se añaden creando un archivo y decorando), **DIP** (el agente depende del `ToolRegistry` abstracto).

#### 2. **Módulo de seguridad (`security/`)**
- **`ThreatDetector`** (interfaz abstracta) – Define el método `check_threat(user_input)`.
  - `PatternThreatDetector` – Implementación que usa expresiones regulares configuradas en `SECURITY_CONFIG`.
- **`SecurityLogger`** (interfaz abstracta) – Define métodos para logging de eventos.
  - `FileSecurityLogger` – Escribe logs en formato JSON en `logs/security/`.
- **Inyección de dependencias** – `main.py` obtiene una instancia de `ThreatDetector` mediante la función `create_threat_detector()`.

*Beneficios arquitectónicos*: **OCP** (se pueden añadir nuevos detectores sin modificar el código existente), **DIP** (la capa de presentación depende de la abstracción `ThreatDetector`), **SRP** (separación entre detección, logging y configuración).

#### 3. **Agente conversacional (`agents.py`)**
- **`run_turn()`** – Maneja el ciclo **pensamiento → herramienta → respuesta**.
- **Integración con el registro de herramientas** – Obtiene la lista de herramientas y el mapa de llamadas desde `ToolRegistry`.
- **Limpieza de `reasoning_content`** – Opcionalmente elimina el contenido de razonamiento del historial para ahorrar tokens.

#### 4. **Punto de entrada (`main.py`)**
- **Bucle interactivo** – Captura entrada del usuario, aplica detección de amenazas, gestiona el flujo de conversación.
- **Prompt modular** – Combina un prompt base con las políticas de seguridad obtenidas de `security_config.py`.
- **Verificación de identidad** – Utiliza la función `check_user_verification_status()` para determinar si el usuario ya ha sido autenticado.

#### 5. **Configuración (`security_config.py`)**
- **`SECURITY_CONFIG`** – Diccionario que define patrones de amenazas y respuestas predefinidas.
- **`get_security_prompt()`** – Devuelve las políticas de seguridad en formato de texto para incluirlas en el prompt del sistema.
- **`create_threat_detector()`** – Factory method que devuelve una instancia configurada de `PatternThreatDetector`.

#### 6. **Persistencia (`assets/`)**
- **Perfiles de usuario** – Archivos `users/<nombre>.ledger` en formato JSON con datos personales y un campo `secret`.
- **Datos de ciudades** – Archivos `cities/<ciudad>.ledger` con información cultural, turística y demográfica.

### Principios SOLID aplicados

| Principio | Cumplimiento | Ejemplo en el código |
|-----------|--------------|----------------------|
| **S**ingle Responsibility | ✅ | Cada módulo tiene una única razón para cambiar: `user_tools.py` solo gestiona usuarios, `detector.py` solo detecta amenazas. |
| **O**pen/Closed | ✅ | El sistema está abierto a extensiones (nuevas herramientas, nuevos detectores) sin modificar código existente (mediante decoradores e interfaces abstractas). |
| **L**iskov Substitution | ✅ | `PatternThreatDetector` puede sustituir a `ThreatDetector`; `FileSecurityLogger` puede sustituir a `SecurityLogger` sin alterar el comportamiento esperado. |
| **I**nterface Segregation | ✅ | Las interfaces son pequeñas y específicas (`ThreatDetector` solo tiene `check_threat`, `SecurityLogger` solo métodos de logging). |
| **D**ependency Inversion | ✅ | Los módulos de alto nivel (`main.py`, `agents.py`) dependen de abstracciones (`ThreatDetector`, `ToolRegistry`), no de implementaciones concretas. |

---

## 📦 Instalación

### Prerrequisitos
- Python 3.10 o superior
- `pip` o `uv` para gestión de dependencias

### Pasos
1. Clona el repositorio (o navega al directorio del proyecto).
2. Crea un entorno virtual:
   ```bash
   python -m venv .venv
   ```
3. Activa el entorno virtual:
   - **Windows (CMD)**: `.venv\Scripts\activate`
   - **Linux/Mac**: `source .venv/bin/activate`
4. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
5. Configura las variables de entorno:
   - Copia el archivo `.env.example` (si existe) a `.env` y edítalo.
   - O crea un archivo `.env` con el siguiente contenido:
     ```env
     DEEPSEEK_API_KEY=tu_clave_api_aquí
     DEEPSEEK_BASE_URL=https://api.deepseek.com
     ```
   - Si no tienes una clave de DeepSeek, puedes obtener una en [DeepSeek Platform](https://platform.deepseek.com/).

---

## ⚙️ Configuración

### Variables de entorno
| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `DEEPSEEK_API_KEY` | Clave de API para autenticar con DeepSeek. | (requerida) |
| `DEEPSEEK_BASE_URL` | URL base de la API de DeepSeek. | `https://api.deepseek.com` |
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram (obtenido de @BotFather). | (opcional, necesario para usar herramientas de Telegram) |
| `TELEGRAM_CHAT_ID` | ID del chat donde enviar mensajes por defecto. | (opcional) |

### Configuración de seguridad
Edita `security_config.py` para ajustar:
- **Patrones de detección** (`SECURITY_CONFIG["patterns"]`) – Expresiones regulares que identifican amenazas.
- **Respuestas predefinidas** (`SECURITY_CONFIG["responses"]`) – Mensajes que el asistente devolverá cuando se detecte una amenaza.
- **Políticas de seguridad** (`SECURITY_CONFIG["security_prompt"]`) – Texto que se inyecta en el prompt del sistema.

---

## 🚀 Uso

### Iniciar el asistente
Ejecuta el script principal:
```bash
python main.py
```

Verás la bienvenida y el banner de seguridad. El asistente estará listo para recibir tus mensajes.

### Flujo típico de conversación
1. **Presentación** – El asistente se presenta como “Andrew Martin”.
2. **Solicitud de nombre** – Pregunta tu nombre (si no lo has proporcionado).
3. **Verificación de identidad** – Si eres un usuario conocido, te pedirá tu “secreto”.
4. **Acceso al perfil** – Una vez verificado, el asistente usará tu perfil internamente para personalizar la conversación (sin revelar datos sensibles).
5. **Ejecución de herramientas** – Puedes hacer preguntas que requieran el uso de herramientas (ej. “¿Qué tiempo hace en Bogotá?”, “Añade un usuario llamado María”, “Envía un mensaje por Telegram a Juan”).
6. **Salida** – Escribe `exit`, `quit` o `bye` para terminar la sesión.

### Comandos especiales
| Comando | Acción |
|---------|--------|
| `exit`, `quit`, `bye`, `adios`, `hasta luego` | Finaliza la conversación y muestra un mensaje de despedida. |
| (vacío) | El asistente preguntará “¿En qué puedo ayudarte?”. |

---

## 📁 Estructura del proyecto

```
Agent-Telegram/
├── main.py                          # Punto de entrada, bucle principal
├── agents.py                        # Lógica del agente conversacional
├── security_config.py               # Configuración de seguridad y factory del detector
├── security_logger.py               # Logger original (mantenido por compatibilidad)
├── requirements.txt                 # Dependencias de Python
├── .env                             # Variables de entorno (no versionado)
├── README.md                        # Este archivo
├── Workflow.md                      # Documentación de flujo de trabajo (FastAPI)
├── verify_add_city.py               # Script de verificación para ciudades
├── assets/                          # Datos persistentes
│   ├── users/                       # Perfiles de usuarios (.ledger)
│   └── cities/                      # Información de ciudades (.ledger)
├── security/                        # Módulo de seguridad refactorizado
│   ├── __init__.py                  # Exporta interfaces e instancia global
│   ├── detector.py                  # ThreatDetector y PatternThreatDetector
│   └── logger.py                    # SecurityLogger y FileSecurityLogger
├── tools/                           # Módulo de herramientas refactorizado
│   ├── registry.py                  # ToolRegistry y decorador @tool
│   ├── user_tools.py                # Herramientas de gestión de usuarios
│   ├── city_tools.py                # Herramientas de información de ciudades
│   ├── datetime_tool.py             # Herramienta de fecha/hora
│   ├── misc_tools.py                # Herramientas misceláneas
│   └── telegram_tool.py             # Herramientas de integración con Telegram
├── test/                            # Suite de pruebas
│   ├── test_tools_refactor.py       # Pruebas del registro de herramientas
│   └── test_security_refactor.py    # Pruebas del módulo de seguridad
├── logs/                            # Logs generados durante la ejecución
│   └── security/                    # Logs de seguridad (JSON con timestamp)
└── docs/                            # Documentación adicional
    ├── Fin_de_semana_de_locura.md   # Ejemplo de plan generado por el asistente
    └── (imágenes y capturas)
```

---

## 🧪 Testing

El proyecto incluye pruebas de integración que validan las refactorizaciones realizadas.

### Ejecutar todas las pruebas
```bash
python -m pytest test/ -v
```
O ejecuta cada archivo individualmente:
```bash
python test/test_tools_refactor.py
python test/test_security_refactor.py
```

### Cobertura de pruebas
- **`test_tools_refactor.py`** – Verifica que el `ToolRegistry` registre correctamente las herramientas, que las funciones se puedan importar y que las herramientas básicas ejecuten sin errores.
- **`test_security_refactor.py`** – Comprueba la importación de los módulos de seguridad, la creación del detector desde configuración, la detección de amenazas con casos conocidos y el funcionamiento del logger.

Los tests también aseguran que las modificaciones respeten los principios SOLID y no rompan la funcionalidad existente.

---

## 🔄 Contribuciones

Las contribuciones son bienvenidas. Si deseas mejorar el proyecto:

1. **Haz un fork** del repositorio.
2. **Crea una rama** para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`).
3. **Realiza tus cambios** siguiendo las convenciones de código existentes.
4. **Añade pruebas** que cubran los nuevos comportamientos.
5. **Ejecuta los tests** para asegurar que nada se rompe.
6. **Envía un pull request** con una descripción clara de los cambios.

### Guías de estilo
- **Nombrado** – Usa `snake_case` para funciones y variables, `CamelCase` para clases.
- **Documentación** – Incluye docstrings en inglés o español para módulos, clases y funciones públicas.
- **Principios SOLID** – Mantén la arquitectura modular y las dependencias invertidas.

---

## 📄 Licencia

Este proyecto está licenciado bajo la **MIT License**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## 🫂 Agradecimientos

- **DeepSeek** – Por proporcionar un modelo de lenguaje potente y accesible.
- **OpenAI** – Por la biblioteca `openai` que facilita la integración con APIs compatibles.
- **Comunidad de Python** – Por las innumerables librerías y buenas prácticas que hacen posible proyectos como este.

---

## 📞 Contacto

Si tienes preguntas, sugerencias o encuentras algún problema, puedes:

- Abrir un **issue** en el repositorio.
- Contactar al mantenedor del proyecto a través de los canales habituales.

**¡Disfruta conversando con Andrew Martin!**