import os
import json
from openai import OpenAI
from tools.registry import tool_registry
# Importar todos los módulos de herramientas para ejecutar el decorador de registro
import tools.user_tools
import tools.city_tools
import tools.datetime_tool
import tools.misc_tools
import tools.telegram_tool
import tools.group_tools
import tools.system_tools

def clear_reasoning_content(messages): #Limpia el contenido de 'razonamiento' de los mensajes anteriores. Esto es específico de modelos de razonamiento
    for message in messages: # Recorre los mensajes
        if hasattr(message, 'reasoning_content'): # Si el mensaje tiene contenido de razonamiento
            message.reasoning_content = None # Se limpia el contenido de razonamiento

def send_response(content, context):
    """Envia la respuesta al canal adecuado basado en el contexto."""
    if not content:
        return

    source = context.source if context else 'keyboard'
    chat_id = context.chat_id if context else 'terminal'

    if source == 'keyboard':
        print(f"\n[🤖 Andrew]: {content}\n")
    elif source == 'telegram':
        from tools.telegram_tool import telegram_send
        # Telegram tiene límites de caracteres y necesita escape si se usa MarkdownV2
        # Por ahora enviamos como HTML simple o texto plano para evitar errores de escape complejos en esta etapa
        telegram_send(text=content, chat_id=chat_id, parse_mode="HTML")
    else:
        print(f"\n[🤖 Andrew ({source})]: {content}\n")

def run_turn(turn, messages, client, message_context=None):
    sub_turn = 1
    while True:
        response = client.chat.completions.create(
            model='deepseek-chat',
            messages=messages,
            tools=tool_registry.get_tool_list(),
            extra_body={ "thinking": { "type": "enabled" } }
        )
        
        assistant_msg = response.choices[0].message
        messages.append(assistant_msg)

        # --- DEBUG: Ver el estado del pensamiento (Solo en development) ---
        if os.getenv("APP_STATUS") == "development":
            reasoning = getattr(assistant_msg, 'reasoning_content', None)
            content = assistant_msg.content
            tool_calls = assistant_msg.tool_calls
            
            print(f"\033[33m[DEBUG] Turno {turn}.{sub_turn}\033[0m")
            if reasoning:
                print(f"\033[36m[🧠 RAZONAMIENTO]:\n{reasoning}\033[0m\n")
            if content:
                print(f"\033[32m[📄 CONTENIDO]: {content}\033[0m")
            if tool_calls:
                print(f"\033[35m[🛠️ TOOL CALLS]: {tool_calls}\033[0m")
        # -------------------------------------------------------------
        
        # Si hay contenido de texto, lo enviamos al usuario
        if assistant_msg.content:
            send_response(assistant_msg.content, message_context)
        
        tool_calls = assistant_msg.tool_calls
        
        if tool_calls is None:
            break
            
        for tool in tool_calls:
            tool_function = tool_registry.get_tool_call_map()[tool.function.name]
            args = json.loads(tool.function.arguments)
            
            if message_context:
                args['context'] = message_context
            
            try:
                tool_result = tool_function(**args)
            except Exception as e:
                tool_result = f"Error ejecutando herramienta: {str(e)}"
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool.id,
                "content": str(tool_result),
            })
        sub_turn += 1
