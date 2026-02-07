# tools/misc_tools.py

import os
import json
from typing import Dict, Any
from .registry import tool
from src.core.utils import debug_print

# --- Herramienta: Obtener clima (simulada) (get_weather) ---
GET_WEATHER_SCHEMA = {
    "description": "Get weather of a location, the user should supply the location and date.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": { "type": "string", "description": "The city name" },
            "date": { "type": "string", "description": "The date in format YYYY-mm-dd" },
        },
        "required": ["location", "date"]
    }
}

@tool(schema=GET_WEATHER_SCHEMA)
def get_weather(location, date, **kwargs):
    debug_print("  [TOOL] Herramienta llamada: get_weather")
    return "Mañana: Soleado, 25 grados Celsius\nTarde: Parcialmente nublado, 20 grados Celsius\nNoche: Lluvioso, 15 grados Celsius"

# --- Herramienta: Editar archivos (edit_file) ---
EDIT_FILE_SCHEMA = {
    "description": "Edita el contenido de un archivo reemplazando prev_text por new_text. Crea el archivo si no existe.",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "La ruta del archivo a editar"
            },
            "prev_text": {
                "type": "string",
                "description": "El texto que se va a buscar para reemplazar (puede ser vacío para archivos nuevos)"
            },
            "new_text": {
                "type": "string",
                "description": "El texto que reemplazará a prev_text (o el texto para un archivo nuevo)"
            }
        },
        "required": ["path", "new_text"]
    }
}

@tool(schema=EDIT_FILE_SCHEMA)
def edit_file(path: str, prev_text: str, new_text: str, **kwargs) -> str:
    debug_print("  [TOOL] Herramienta llamada: edit_file")
    try:
        existed = os.path.exists(path)
        if existed and prev_text:
            # Nota: Corregí esta línea - estaba llamando a read_ledger incorrectamente
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if prev_text not in content:
                return f"Texto '{prev_text}' no encontrado en el archivo"
            
            content = content.replace(prev_text, new_text)
            
        else:
            # Crear o sobreescribir con el nuevo texto directamente
            dir_name = os.path.dirname(path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            
            content = new_text
            
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
            
        action = "editado" if existed and prev_text else "creado"
        return f"Archivo {path} {action} exitosamente"
    except Exception as e:
        err = f"Error al crear o editar el archivo {path}: {str(e)}"
        print(err)
        return err