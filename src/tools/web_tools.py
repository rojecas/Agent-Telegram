# tools/web_tools.py

import json
import requests
from typing import Dict, Any, List
from .registry import tool
from src.core.utils import benchmark

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
    print(f"  ⚙️ Herramienta llamada: web_search ('{query}')")
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
    print(f"  ⚙️ Herramienta llamada: read_url ('{url}')")
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
