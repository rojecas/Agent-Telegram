- Busca a BotFather en Telegram (usando el teléfono)
- Haz clic en [Start]
- Puedes ver toda la ayuda para este bot
- Escribe /new en el chat
- Copia el token de acceso a la API (el número después de ":")
- Dale un nombre y un nombre de usuario (que termine con _bot) a tu bot
- Agrega tu bot a tu lista de contactos
- Ve a: https://api.telegram.org/bot{}/getUpdates




# Cómo obtener el Chat ID de un Bot de Telegram

**Contenido:**
1. [Crear un Bot de Telegram y obtener un Token del Bot](#crear-un-bot-de-telegram-y-obtener-un-token-del-bot)
1. [Obtener Chat ID para un Chat Privado](#obtener-chat-id-para-un-chat-privado)
1. [Obtener Chat ID para un Canal](#obtener-chat-id-para-un-canal)
1. [Obtener Chat ID para un Chat Grupal](#obtener-chat-id-para-un-chat-grupal)
1. [Obtener Chat ID para un Tema en un Chat Grupal](#obtener-chat-id-para-un-tema-en-un-chat-grupal)

## Crear un Bot de Telegram y obtener un Token del Bot

1. Abre la aplicación de Telegram y busca `@BotFather`
1. Haz clic en Start
1. Haz clic en Menu -> /newbot o escribe `/newbot` y presiona Enviar
1. Sigue las instrucciones hasta que recibas un mensaje como este:
    ```
    Done! Congratulations on your new bot. You will find it at t.me/new_bot.
    You can now add a description.....

    Use this token to access the HTTP API:
    63xxxxxx71:AAFoxxxxn0hwA-2TVSxxxNf4c
    Keep your token secure and store it safely, it can be used by anyone to control your bot.

    For a description of the Bot API, see this page: https://core.telegram.org/bots/api
    ```
1. Aquí está nuestro token del bot `63xxxxxx71:AAFoxxxxn0hwA-2TVSxxxNf4c` (asegúrate de no compartirlo con nadie).

[Volver arriba ↑](#cómo-obtener-el-chat-id-de-un-bot-de-telegram)

## Obtener Chat ID para un Chat Privado

1. Busca y abre tu nuevo bot de Telegram
1. Haz clic en Start o envía un mensaje
1. Abre esta URL en un navegador `https://api.telegram.org/bot{tu_token_del_bot}/getUpdates` 
    - Nota que necesitamos prefijar nuestro token con la palabra `bot`
    - Ej: `https://api.telegram.org/bot63xxxxxx71:AAFoxxxxn0hwA-2TVSxxxNf4c/getUpdates`
1. Verás un JSON como este:
    ```
    {
      "ok": true,
      "result": [
        {
          "update_id": 83xxxxx35,
          "message": {
            "message_id": 2643,
            "from": {...},
            "chat": {
              "id": 21xxxxx38,
              "first_name": "...",
              "last_name": "...",
              "username": "@username",
              "type": "private"
            },
            "date": 1703062972,
            "text": "/start"
          }
        }
      ]
    }
    ```
1. Verifica el valor de `result.0.message.chat.id`, y aquí está nuestro Chat ID: `21xxxxx38`
3. Intentemos enviar un mensaje: `https://api.telegram.org/bot63xxxxxx71:AAFoxxxxn0hwA-2TVSxxxNf4c/sendMessage?chat_id=21xxxxx38&text=test123`
4. Cuando configuremos correctamente el token del bot y el chat ID, el mensaje `test123` debería llegar a nuestro chat del bot de Telegram.

[Volver arriba ↑](#cómo-obtener-el-chat-id-de-un-bot-de-telegram)

## Obtener Chat ID para un Canal

1. Agrega tu bot de Telegram a un canal
1. Envía un mensaje al canal
1. Abre esta URL `https://api.telegram.org/bot{tu_token_del_bot}/getUpdates`
1. Verás un JSON como este:
    ```
    {
      "ok": true,
      "result": [
        {
          "update_id": 838xxxx36,
          "channel_post": {...},
            "chat": {
              "id": -1001xxxxxx062,
              "title": "....",
              "type": "channel"
            },
            "date": 1703065989,
            "text": "test"
          }
        }
      ]
    }
    ```
1. Verifica el valor de `result.0.channel_post.chat.id`, y aquí está nuestro Chat ID: `-1001xxxxxx062`
1. Intentemos enviar un mensaje: `https://api.telegram.org/bot63xxxxxx71:AAFoxxxxn0hwA-2TVSxxxNf4c/sendMessage?chat_id=-1001xxxxxx062&text=test123`
1. Cuando configuremos correctamente el token del bot y el chat ID, el mensaje `test123` debería llegar a nuestro canal de Telegram.

[Volver arriba ↑](#cómo-obtener-el-chat-id-de-un-bot-de-telegram)

## Obtener Chat ID para un Chat Grupal

La forma más fácil de obtener un ID de chat grupal es a través de la aplicación de escritorio de Telegram.

1. Abre Telegram en una aplicación de escritorio
1. Agrega tu bot de Telegram a un grupo de chat
1. Envía un mensaje al grupo de chat
1. Haz clic derecho en el mensaje y haz clic en `Copiar enlace del mensaje`
    - Obtendrás un enlace como este: `https://t.me/c/194xxxx987/11/13`
    - El patrón: `https://t.me/c/{group_chat_id}/{group_topic_id}/{message_id}`
    - Así que aquí está nuestro Chat ID: `194xxxx987`
1. Para usar el ID del chat grupal en la API, necesitamos prefijarlo con el número `-100`, así: `-100194xxxx987`
1. Ahora intentemos enviar un mensaje: `https://api.telegram.org/bot63xxxxxx71:AAFoxxxxn0hwA-2TVSxxxNf4c/sendMessage?chat_id=-100194xxxx987&text=test123`
1. Cuando configuremos correctamente el token del bot y el chat ID, el mensaje `test123` debería llegar a nuestro chat grupal.

[Volver arriba ↑](#cómo-obtener-el-chat-id-de-un-bot-de-telegram)

---

# Funcionalidades de Telegram de Andrew (v2.0)

Con la implementación de la Fase 3, Andrew tiene herramientas específicas para interactuar con Telegram de forma más inteligente:

- **Búsqueda de Miembros**: Andrew puede listar los miembros de un grupo para conocer el contexto social.
- **Introspección**: Andrew sabe su propio nombre de usuario, su ID y en qué chats ha estado activo.
- **Auto-Discovery**: Al iniciar, Andrew recupera automáticamente la lista de grupos y chats privados registrados anteriormente.
- **Privacy Firewall**: Andrew detecta si está en un grupo o en un chat privado y filtra la información sensible en consecuencia.

Para verificar estas funciones, puedes preguntarle:
- "¿Andrew, quiénes somos en este grupo?"
- "¿En qué chats has estado trabajando?"
- "¿Cuál es tu nombre de usuario en Telegram?"

## Obtener Chat ID para un Tema en un Chat Grupal

Para enviar un mensaje a un tema específico en un grupo de Telegram, necesitamos obtener el ID del tema.

1. Similar a los pasos anteriores, después de hacer clic en `Copiar enlace del mensaje`, obtendremos un enlace como: `https://t.me/c/194xxxx987/11/13`, por lo que el ID del tema del grupo es `11`.
1. Ahora podemos usarlo así (ver `message_thread_id`): `https://api.telegram.org/bot783114779:XXXXXXXXXXXXXX-NmvHN3OPc/sendMessage?chat_id=-100194xxxx987&message_thread_id=11&text=test123`
1. Cuando configuremos correctamente el token del bot y el chat ID, el mensaje `test123` debería llegar dentro del tema del chat grupal.
    
[Volver arriba ↑](#cómo-obtener-el-chat-id-de-un-bot-de-telegram)