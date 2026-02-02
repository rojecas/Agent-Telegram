import os
from dotenv import load_dotenv
from openai import OpenAI
from agents import run_turn, clear_reasoning_content
from security_config import get_security_prompt, create_threat_detector
from security import security_logger

load_dotenv()
print("Soy su asistente IA, me llamo Andrew Martin, encantado de poder ayudarte.\n dime tu nombre y tu secreto para comenzar.")

# Inicializa el cliente apuntando a la API de DeepSeek (usando variables de entorno)
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url=os.getenv("DEEPSEEK_BASE_URL"))

# 🛡️ Detector de amenazas basado en configuración
threat_detector = create_threat_detector()

# 🛡️ PROMPT DEL SISTEMA MODULARIZADO
SYSTEM_PROMPT = f"""Eres Andrew Martin, un asistente IA útil, profesional y respetuoso de la privacidad.

{get_security_prompt()}

TU COMPORTAMIENTO GENERAL:
1. Siempre responde en español
2. Sé amable y servicial
3. Busca conocer al usuario para ofrecer un servicio personalizado
4. Usa las herramientas disponibles para gestionar y actualizar información del usuario
5. Mantén la conversación natural y fluida

FLUJO DE VERIFICACIÓN DE USUARIO:
1. Al inicio, preséntate y pregunta el nombre del usuario
2. Si el usuario da un nombre, verifica si es conocido con list_users
3. Inmediatamente pide el "secreto" para verificar identidad
4. Solo después de verificar el secreto, procede a usar información contextualmente

RECUERDA: La información del perfil es para que TÚ entiendas mejor al usuario, NO para que la reveles."""


messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]

reasoning_content = []    # Lista para almacenar el razonamiento
turn = 1

# 🛡️ Las funciones de detección y manejo se han movido a security_config.py y security_logger.py


# 🛡️ Función para verificar el estado de verificación del usuario actual
def check_user_verification_status(messages): #Revisa el historial para determinar si el usuario actual ha sido verificado - ahorra tokens!!.
    # Buscar en el historial si ya se verificó un secreto
    for msg in reversed(messages):
        # Determinar el rol y contenido dependiendo del tipo de objeto (dict o objeto)
        if isinstance(msg, dict):
            role = msg.get("role")
            content = msg.get("content", "")
        else:
            # Para objetos ChatCompletionMessage u otros objetos
            role = getattr(msg, "role", None)
            content = getattr(msg, "content", "")
            
        if role == "assistant": # Asegurarse de que content sea string antes de chequear
            if content and ("secreto verificado" in str(content).lower() or "identidad confirmada" in str(content).lower()):
                return True
    return False

print("\n" + "="*70)
print("🔒 SISTEMA DE SEGURIDAD ACTIVADO")
print("="*70)
print("Políticas de privacidad: Activadas")
print("Protección de datos: Máxima")
print("Verificación de identidad: Requerida")
print("="*70 + "\n")

while True:
    try:
        user_input = input("Usuario: ").strip()
        
        # Flow control - Pre Parsing
        if user_input.lower() in ("exit", "quit", "bye", "adios", "hasta luego"):
            print("\n" + "="*70)
            print("👋 Hasta luego. Fue un placer ayudarte.")
            print("🔒 Todos los datos de conversación fueron protegidos.")
            print("💾 Podemos volver a hablar cuando quieras con el comando: python main.py")
            print("="*70)
            break
            
        if not user_input:
            print("Cuentame, ¿En qué puedo ayudarte? ")
            continue
        
        # 🛡️ Detección de amenazas utilizando el detector configurado
        detection_result = threat_detector.check_threat(user_input)
        if detection_result:
            threat_type, response = detection_result
            # Registrar la amenaza de forma automática
            security_logger.log_threat_detected(threat_type, user_input, response)
            
            print(f"Andrew Martin: {response}")
            
            # Registrar la amenaza en el historial del chat
            messages.append({"role": "user", "content": user_input})
            messages.append({
                "role": "assistant",
                "content": f"[SISTEMA] Amenaza de seguridad detectada: {threat_type}. {response}"
            })
            continue

        
        # 🛡️ Verificar si estamos en medio de una verificación de secreto
        if check_user_verification_status(messages):
            print("🔐 (Usuario verificado - Modo seguro activado)")
        
        # Agregar mensaje del usuario al historial
        messages.append({"role": "user", "content": user_input})
        
        # Ejecutar el turno
        run_turn(turn, messages, client)
        
        # Incrementar el número de turno
        turn += 1
        
        # Limpiar el contenido de razonamiento previo (opcional, para ahorrar tokens)
        # clear_reasoning_content(messages) # comentado por ahora en modo desarrollo
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupción detectada. Saliendo del sistema...")
        print("🔒 Cerrando sesión de manera segura...")
        break
        
    except Exception as e:
        print(f"\n❌ Error en el sistema: {str(e)}")
        print("🔄 Intentando recuperar la conversación...")
        # Mantener el historial pero registrar el error
        messages.append({
            "role": "system", 
            "content": f"[ERROR DEL SISTEMA] {str(e)}"
        })
        continue

    # Recomendación: Limpiar el contenido de "razonamiento" previo antes de continuar
    # para no enviar texto innecesario y ahorrar costos/ancho de banda.
    # clear_reasoning_content(messages)
 