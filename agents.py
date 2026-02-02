import json
from openai import OpenAI
from tools.registry import tool_registry
# Importar todos los módulos de herramientas para ejecutar el decorador de registro
import tools.user_tools
import tools.city_tools
import tools.datetime_tool
import tools.misc_tools
import tools.telegram_tool

def clear_reasoning_content(messages): #Limpia el contenido de 'razonamiento' de los mensajes anteriores. Esto es específico de modelos de razonamiento
    for message in messages: # Recorre los mensajes
        if hasattr(message, 'reasoning_content'): # Si el mensaje tiene contenido de razonamiento
            message.reasoning_content = None # Se limpia el contenido de razonamiento

def run_turn(turn, messages, client): #Ejecuta un turno de conversación. Maneja el bucle de pensamiento -> herramienta -> respuesta.
    sub_turn = 1
    while True:
        # Llama a la API (en este caso DeepSeek)
        response = client.chat.completions.create(
            model='deepseek-chat',
            messages=messages,
            tools=tool_registry.get_tool_list(),  # Ahora obtenemos la lista de esquemas desde el registro
            # Configuración extra específica para activar el modo de "pensamiento" (thinking)
            extra_body={ "thinking": { "type": "enabled" } }
        )
        
        # Agrega la respuesta del asistente al historial de mensajes
        messages.append(response.choices[0].message)
        
        # Extrae partes de la respuesta
        reasoning_content = response.choices[0].message.reasoning_content  # El proceso de pensamiento interno
        content = response.choices[0].message.content  # La respuesta final al usuario (si la hay)
        tool_calls = response.choices[0].message.tool_calls  # Solicitudes de uso de herramientas (si las hay)
        
        # Imprime lo que está pasando en consola para depuración - solo para desarrollo o para entender el funcionamiento
        print(f"'\033[33m'Turn {turn}.{sub_turn}\n{reasoning_content=}\n{content=}\n{tool_calls=}'\033[0m'")
        
        # CONDICIÓN DE PARADA: Si el modelo no pide usar herramientas, significa que ya tiene la respuesta final.
        if tool_calls is None:
            print(f"'\033[32m'\n{content}'\033[0m'")
            break
            
        # Si hay llamadas a herramientas, las ejecutamos
        for tool in tool_calls:
            # Busca la función Python correspondiente en nuestro mapa
            tool_function = tool_registry.get_tool_call_map()[tool.function.name]
            # Ejecuta la función pasando los argumentos que el modelo extrajo (convertidos de JSON)
            tool_result = tool_function(**json.loads(tool.function.arguments))
            
            # print(f"tool result for {tool.function.name}: {tool_result}\n") # Codigo para depuracion
            
            # Agrega el resultado de la herramienta al historial para que el modelo lo "lea" en la siguiente vuelta
            messages.append({
                "role": "tool",  # Rol específico para respuestas de herramientas
                "tool_call_id": tool.id,  # ID para vincular la respuesta con la petición original
                "content": str(tool_result),
            })
            print(f"'\033[31m'messages={messages}'\033[0m'")
        sub_turn += 1
