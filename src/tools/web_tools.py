# tools/web_tools.py

import json
import requests
from typing import Dict, Any, List
from .registry import tool
from src.core.utils import benchmark, debug_print

try:
    from ddgs import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    try:
        from duckduckgo_search import DDGS
        DDGS_AVAILABLE = True
    except ImportError:
        DDGS_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# --- Herramienta: Búsqueda web (web_search) ---
WEB_SEARCH_SCHEMA = {
    "description": "Realiza una búsqueda en la web utilizando DuckDuckGo y devuelve los primeros resultados. Úsala para obtener información actualizada, noticias, definiciones o datos que no están almacenados localmente.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Término(s) de búsqueda (ej: 'noticias de tecnología', 'clima en Bogotá')."
            }
        },
        "required": ["query"]
    }
}

@benchmark
@tool(schema=WEB_SEARCH_SCHEMA)
def web_search(query: str, **kwargs) -> str:
    debug_print(f"  [TOOL] Herramienta llamada: web_search ('{query}')")
    try:
        if not DDGS_AVAILABLE:
            return json.dumps({
                "error": "La biblioteca 'ddgs' (o 'duckduckgo-search') no está instalada. Instálala con: pip install ddgs"
            }, ensure_ascii=False)

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            if not results:
                return json.dumps({
                    "message": f"No se encontraron resultados para la búsqueda '{query}'."
                }, ensure_ascii=False)

            # Formatear resultados
            formatted = [
                {
                    "title": r.get("title", ""),
                    "link": r.get("href", ""),
                    "snippet": r.get("body", "")
                }
                for r in results
            ]
            return json.dumps({"results": formatted}, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": f"Error durante la búsqueda web: {str(e)}"
        }, ensure_ascii=False)

# --- Herramienta: Leer contenido de URL (read_url) ---
READ_URL_SCHEMA = {
    "description": "Obtiene el contenido textual de una página web, eliminando HTML y elementos de navegación. Úsala para leer artículos, documentación o cualquier página web cuyo contenido necesites analizar.",
    "parameters": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL completa de la página a leer (ej: 'https://example.com/article')."
            }
        },
        "required": ["url"]
    }
}

@benchmark
@tool(schema=READ_URL_SCHEMA)
def read_url(url: str, **kwargs) -> str:
    debug_print(f"  [TOOL] Herramienta llamada: read_url ('{url}')")
    try:
        if not BS4_AVAILABLE:
            return json.dumps({
                "error": "La biblioteca 'beautifulsoup4' no está instalada. Instálala con: pip install beautifulsoup4"
            }, ensure_ascii=False)

        # Realizar la petición HTTP
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parsear contenido con BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Eliminar scripts, estilos, etiquetas no deseadas
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.decompose()

        # Obtener texto y limpiar espacios extra
        text = soup.get_text(separator="\n")
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        cleaned = "\n".join(chunk for chunk in chunks if chunk)

        # Limitar longitud (para no exceder límites de contexto)
        max_length = 8000
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "\n...[contenido truncado]"

        return json.dumps({
            "url": url,
            "status": response.status_code,
            "content": cleaned
        }, ensure_ascii=False)
    except requests.exceptions.RequestException as e:
        return json.dumps({
            "error": f"Error al acceder a la URL: {str(e)}"
        }, ensure_ascii=False)
    except Exception as e:
         return json.dumps({
             "error": f"Error inesperado al leer la URL: {str(e)}"
         }, ensure_ascii=False)

# --- Herramienta: Enviar documento por Telegram (telegram_send_document) ---
TELEGRAM_SEND_DOCUMENT_SCHEMA = {
    "description": "Envía un documento (archivo) a un chat de Telegram. Puede enviar archivos locales o desde una URL. Úsala cuando el usuario solicite compartir un archivo, documento, imagen u otro tipo de archivo.",
    "parameters": {
        "type": "object",
        "properties": {
            "chat_id": {
                "type": "string",
                "description": "ID del chat de Telegram. Si no se proporciona, se usará el CHAT_ID por defecto del entorno."
            },
            "document": {
                "type": "string",
                "description": "Ruta local del archivo o URL del documento a enviar."
            },
            "caption": {
                "type": "string",
                "description": "Texto descriptivo que acompaña al documento (opcional)."
            },
            "parse_mode": {
                "type": "string",
                "description": "Modo de parseo para el caption: 'MarkdownV2', 'HTML', o 'Markdown'.",
                "enum": ["MarkdownV2", "HTML", "Markdown"]
            }
        },
        "required": ["document"]
    }
}

@tool(schema=TELEGRAM_SEND_DOCUMENT_SCHEMA)
def telegram_send_document(document: str, chat_id: str = None, caption: str = "", parse_mode: str = "MarkdownV2", **kwargs) -> str:
    """
    Envía un documento a un chat de Telegram.
    """
    debug_print(f"  [TOOL] Herramienta llamada: telegram_send_document (document={document})")
    
    try:
        import os
        import requests
        from dotenv import load_dotenv
        
        load_dotenv()
        TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        
        if not TELEGRAM_BOT_TOKEN:
            return json.dumps({
                "success": False,
                "error": "Token de bot de Telegram no configurado. Agregue TELEGRAM_BOT_TOKEN al archivo .env"
            }, ensure_ascii=False)
        
        # Determinar chat_id
        target_chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        if not target_chat_id:
            return json.dumps({
                "success": False,
                "error": "Se requiere chat_id. Proporcione un chat_id o configure TELEGRAM_CHAT_ID en .env"
            }, ensure_ascii=False)
        
        TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
        
        # Preparar datos según si es archivo local o URL
        if document.startswith(('http://', 'https://')):
            # Es una URL
            payload = {
                "chat_id": target_chat_id,
                "document": document
            }
            if caption:
                payload["caption"] = caption
                payload["parse_mode"] = parse_mode
            
            response = requests.post(f"{TELEGRAM_API_BASE}/sendDocument", json=payload, timeout=30)
        else:
            # Es un archivo local
            if not os.path.exists(document):
                return json.dumps({
                    "success": False,
                    "error": f"Archivo no encontrado: {document}"
                }, ensure_ascii=False)
            
            with open(document, 'rb') as file:
                files = {'document': file}
                data = {
                    "chat_id": target_chat_id
                }
                if caption:
                    data["caption"] = caption
                    data["parse_mode"] = parse_mode
                
                response = requests.post(f"{TELEGRAM_API_BASE}/sendDocument", data=data, files=files, timeout=30)
        
        result = response.json()
        
        if result.get("ok"):
            return json.dumps({
                "success": True,
                "message": "Documento enviado exitosamente",
                "message_id": result["result"]["message_id"],
                "chat_id": result["result"]["chat"]["id"],
                "file_name": result["result"]["document"]["file_name"] if "document" in result["result"] else "N/A"
            }, ensure_ascii=False)
        else:
            return json.dumps({
                "success": False,
                "error": f"Error de Telegram API: {result.get('description', 'Unknown error')}"
            }, ensure_ascii=False)
            
    except requests.exceptions.RequestException as e:
        return json.dumps({
            "success": False,
            "error": f"Error de conexión: {str(e)}"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error inesperado: {str(e)}"
        }, ensure_ascii=False)
