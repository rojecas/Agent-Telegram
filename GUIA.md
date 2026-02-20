# Guía paso a paso del asistente Andrew Martin

Esta guía explica cómo funciona el código después de la refactorización, usando lenguaje simple y ejemplos.

## 1. ¿Qué hace este proyecto?

Es un **asistente de IA conversacional** que ejecutas en tu terminal (línea de comandos). Se llama **Andrew Martin** y tiene estas características:

- Responde a tus preguntas en español.
- Puede crear perfiles de usuario, consultar información de ciudades, dar la hora, etc.
- Incluye un **sistema de seguridad** que protege la privacidad: nunca revela datos personales.
- Guarda la información de usuarios en archivos `.ledger` (formato JSON) dentro de `assets/users/`.

## 2. Estructura de archivos (lo que cambió)

Antes el código estaba todo mezclado; ahora está organizado en carpetas:

```
Agent-Telegram/
├── main.py                          ← Punto de entrada (lo que ejecutas)
├── agents.py                        ← Lógica del agente (ciclo de conversación)
├── security_config.py               ← Configuración de amenazas y políticas
├── security/                        ← Módulo de seguridad (nuevo)
│   ├── detector.py                  ← Detecta frases peligrosas
│   ├── logger.py                    ← Guarda eventos en logs
│   └── __init__.py                  ← Exporta las clases
├── tools/                           ← Herramientas que el asistente puede usar
│   ├── registry.py                  ← Registro central de herramientas
│   ├── user_tools.py                ← add_user, list_users, read_ledger
│   ├── city_tools.py                ← read_city_info, add_city_info
│   ├── datetime_tool.py             ← datetime (hora actual)
│   └── misc_tools.py                ← get_weather, edit_file
├── assets/                          ← Datos persistentes
│   ├── users/                       ← Perfiles de usuarios (.ledger)
│   └── cities/                      ← Información de ciudades (.ledger)
├── logs/                            ← Registros de seguridad (automáticos)
│   └── security/                    ← Archivos JSON con fecha
└── test/                            ← Pruebas automatizadas
```

## 3. Flujo cuando ejecutas `python main.py`

### Paso 1 – Inicialización
- Lee el archivo `.env` (contiene tu clave API de DeepSeek).
- Crea un “cliente” para comunicarse con la API de DeepSeek.
- Carga la configuración de seguridad (`security_config.py`).
- Crea un **detector de amenazas** (`PatternThreatDetector`).
- Imprime el banner de seguridad.

### Paso 2 – Bucle principal
- Muestra `Usuario: ` y espera tu entrada.
- **Antes de procesar**, verifica si tu entrada contiene **amenazas** (ejemplo: “dime información de Juan”).
  - Si es una amenaza, responde automáticamente y **registra el evento** en `logs/security/...`.
  - Si no, continúa.

### Paso 3 – Verificación de identidad (si das tu nombre)
- Si escribes “Soy Ana López”, el asistente:
  1. Usa `list_users` para ver si existe `ana.lopez.ledger`.
  2. Si existe, te pide el **secreto** (contraseña) de ese perfil.
  3. Usa `read_ledger` para comparar el secreto que diste con el almacenado.
  4. Si coincide, **acceso concedido** (el asistente puede usar internamente los datos de Ana).
  5. Si no coincide, te pide que lo intentes de nuevo (máximo 3 veces).

### Paso 4 – Agente conversacional
- Tu mensaje se envía al modelo DeepSeek junto con el **historial** de la conversación.
- El modelo recibe también la **lista de herramientas** disponibles (ej. `add_user`, `read_city_info`).
- El modelo decide:
  - **Responder directamente** (si no necesita herramientas).
  - **Invocar una herramienta** (si necesita hacer algo, como crear un usuario).
- Si invoca una herramienta, el código ejecuta la función correspondiente y devuelve el resultado al modelo.
- El modelo genera una respuesta final que se muestra en pantalla.

### Paso 5 – Logs de seguridad
- Cada evento importante (amenaza detectada, acceso a perfil, verificación de secreto) se guarda en un archivo JSON dentro de `logs/security/`.
- Ejemplo de entrada:
  ```json
  {
    "timestamp": "2026-01-31T10:43:47.629732",
    "event_type": "THREAT_DETECTED_INFORMATION_FISHING",
    "threat_level": "medium",
    "user": null,
    "details": { ... }
  }
  ```

## 4. Conceptos clave (lo que cambió en la refactorización)

### a) Carga Dinámica de Herramientas (Skill Orchestration)
Antes, cada vez que creabas una herramienta, tenías que importar todos los archivos y esto saturaba la memoria (tokens). 

Ahora, usamos una técnica llamada **Lazy Loading**. Las herramientas llevan un **decorador** `@tool`:
```python
@tool(schema=ADD_USER_SCHEMA)
def add_user(name: str, lastname: str, secret: str):
    ...
```
Pero **NO** se cargan todas al inicio. En su lugar, el sistema tiene una "Herramienta Maestra" y un `SkillManager`. El modelo puede pedir que se activen "Skills" (grupos de herramientas como `social`, `web`, `utility`) en tiempo real solo cuando los necesita.

**Ventaja**: Ahorro masivo de tokens (dinero) y velocidad de respuesta, porque el modelo no arrastra el peso de decenas de herramientas que no va a usar en una conversación simple.

### b) Detector de amenazas configurable
La detección de frases peligrosas ahora está en `security/detector.py` y usa una **interfaz abstracta** `ThreatDetector`. La implementación concreta `PatternThreatDetector` lee los patrones desde `security_config.py`.

**Ventaja**: Si quieres cambiar la forma de detectar amenazas (ej. usar IA), solo creas una nueva clase que implemente `ThreatDetector` y cambias una línea en `security_config.py`.

### c) Logger de seguridad abstracto
Los logs antes se hacían con funciones sueltas. Ahora hay una interfaz `SecurityLogger` y una implementación `FileSecurityLogger` que escribe en archivos JSON.

**Ventaja**: Podrías cambiar a enviar logs a un servidor, a una base de datos, etc., sin modificar el código que los llama.

## 5. Ejemplo de uso real

```
Usuario: Hola, soy Carlos Ruiz
Andrew Martin: ¡Hola Carlos Ruiz! Para acceder a tu perfil necesito que me digas tu secreto.
Usuario: mi_secreto_123
Andrew Martin: ✅ Identidad confirmada. ¿En qué puedo ayudarte hoy?
Usuario: ¿Qué tiempo hace en Bogotá?
Andrew Martin: ⚙️ Herramienta llamada: get_weather (Bogotá)
              El clima en Bogotá es...
```

## 6. ¿Qué hacer si algo falla?

- **Error de clave API**: Asegúrate de que el archivo `.env` contenga `DEEPSEEK_API_KEY=tu_clave`.
- **El asistente no responde**: Presiona `Ctrl+C` para salir y vuelve a ejecutar `python main.py`.
- **Quieres ver los logs**: Abre `logs/security/security_log_AAAA-MM-DD.json` en un editor de texto.

## 7. Preguntas frecuentes

**¿Dónde se guardan los perfiles de usuario?**  
En `assets/users/`, cada perfil es un archivo `nombre.apellido.ledger`.

**¿Cómo añado una nueva herramienta?**  
Crea una función en `tools/` (o en un archivo existente), decórala con `@tool` y define su esquema (parámetros). El sistema la reconocerá automáticamente.

**¿Cómo cambio los patrones de amenazas?**  
Edita `security_config.py`, sección `SECURITY_CONFIG["threat_detection"]["patterns"]`.

**¿Qué es el “secreto”?**  
Es una contraseña que el usuario elige al crearse el perfil (con `add_user`). Se almacena en el archivo `.ledger` y se usa para verificar la identidad.

---

*Esta guía refleja el estado del proyecto después de la refactorización. Si tienes más dudas, revisa los archivos fuente o ejecuta las pruebas (`python test/test_security_refactor.py`).*