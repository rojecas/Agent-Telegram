# tools/city_tools.py

import os
import json
from typing import Dict, Any, List
from .registry import tool
from src.agent_telegram.core.utils import benchmark

# Estructura base para nuevas ciudades
CITY_TEMPLATE = {
    "atractivos_culturales": [],
    "espacios_publicos": [],
    "parques_y_naturaleza": [],
    "experiencias_gastronomicas": [],
    "unidades_deportivas": [],
    "centros_academicos": [],
    "centros_comerciales": []
}

# --- Herramienta: Leer información de ciudad (read_city_info) ---
READ_CITY_INFO_SCHEMA = {
    "description": "Obtiene información detallada sobre una ciudad específica leyendo su archivo ledger. Úsala SIEMPRE que necesites conocer detalles sobre atractivos, parques, gastronomía o universidades de una ciudad. Es mucho más eficiente que leer archivos genéricos.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "El nombre de la ciudad a consultar (ej: 'cali', 'bogota', 'pereira')."
            }
        },
        "required": ["city"]
    }
}

@benchmark
@tool(schema=READ_CITY_INFO_SCHEMA)
def read_city_info(city: str, **kwargs) -> str:
    print(f"  ⚙️ Herramienta llamada: read_city_info ({city})")
    try:
        city_lower = city.lower().strip()
        file_path = f"./assets/cities/{city_lower}.ledger"
        
        if not os.path.exists(file_path):
            return json.dumps({"error": f"No se encontró información para la ciudad: {city}. Puedes usar add_city_info para crearla."}, ensure_ascii=False)
            
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        return json.dumps(data, indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        return json.dumps({"error": f"Error: El archivo de datos de {city} está corrupto."})
    except Exception as e:
        return json.dumps({"error": f"Error al leer información de ciudad: {str(e)}"})

# --- Herramienta: Agregar información a ciudad (add_city_info) ---
ADD_CITY_INFO_SCHEMA = {
    "description": "Agrega, actualiza o CREA información de una ciudad. Si la ciudad no existe, esta herramienta la creará automáticamente con la estructura correcta. Úsala para guardar nuevos puntos de interés, recomendaciones o datos de contacto en una ciudad. NO uses edit_file para esto.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "Nombre de la ciudad (ej: 'pereira', 'armenia')."
            },
            "info_json": {
                "type": "string",
                "description": "JSON String con la estructura {'categoria': [{'nombre': '...', 'descripcion': '...'}]}. Categorías válidas: atractivos_culturales, espacios_publicos, parques_y_naturaleza, experiencias_gastronomicas, unidades_deportivas, centros_academicos, centros_comerciales."
            }
        },
        "required": ["city", "info_json"]
    }
}

@tool(schema=ADD_CITY_INFO_SCHEMA)
def add_city_info(city: str, info_json: str, **kwargs):
    print(f"  ⚙️ Herramienta llamada: add_city_info ({city})")
    try:
        city_lower = city.lower().strip()
        os.makedirs("./assets/cities", exist_ok=True)
        file_path = f"./assets/cities/{city_lower}.ledger"
        
        # Cargar o inicializar datos
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            # Crear nueva ciudad con el template estándar
            data = {city_lower: CITY_TEMPLATE.copy()}
            print(f"  🆕 Creando nuevo ledger para la ciudad: {city_lower}")
            
        try:
            new_info = json.loads(info_json)
        except json.JSONDecodeError:
            return json.dumps({"error": "El argumento info_json no es un JSON válido."})

        # Buscar la estructura correcta de la ciudad dentro del archivo
        if city_lower in data:
            city_data = data[city_lower]
        else:
            # Si el archivo existe pero no tiene el nombre de la ciudad como llave raíz
            if len(data) == 1 and isinstance(list(data.values())[0], dict):
                city_key = list(data.keys())[0]
                city_data = data[city_key]
            else:
                city_data = data # Estructura plana

        changes_made = False
        messages = []

        for category, items in new_info.items():
            if category not in city_data:
                city_data[category] = []
            
            if not isinstance(items, list):
                 messages.append(f"⚠️ Categoría '{category}' ignorada porque el valor no es una lista.")
                 continue

            for new_item in items:
                if not isinstance(new_item, dict) or "nombre" not in new_item:
                     messages.append(f"⚠️ Item ignorado en '{category}' porque no tiene 'nombre' o no es un objeto.")
                     continue
                
                # Buscar si el elemento ya existe
                existing_item = next((item for item in city_data[category] if isinstance(item, dict) and item.get("nombre") == new_item["nombre"]), None)
                
                if existing_item:
                    # Lógica de actualización
                    updated_fields = []
                    for key, value in new_item.items():
                        if key == "nombre": continue
                        
                        # Si ambos son listas, combinar elementos
                        if isinstance(value, list) and isinstance(existing_item.get(key), list):
                             for v in value:
                                 if v not in existing_item[key]:
                                     existing_item[key].append(v)
                                     updated_fields.append(f"{key} (item agregado)")
                        # Actualizar valor si es diferente
                        elif existing_item.get(key) != value:
                             existing_item[key] = value
                             updated_fields.append(key)
                    
                    if updated_fields:
                        messages.append(f"🔄 Actualizado '{new_item['nombre']}' en '{category}': {', '.join(updated_fields)}")
                        changes_made = True
                    else:
                        messages.append(f"ℹ️ '{new_item['nombre']}' ya existe en '{category}' sin cambios.")
                        
                else:
                    # Agregar nuevo elemento
                    city_data[category].append(new_item)
                    messages.append(f"✅ Agregado '{new_item['nombre']}' a '{category}'.")
                    changes_made = True

        # Si se creó el archivo por primera vez, siempre guardamos
        if changes_made or not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return json.dumps({"success": True, "details": messages}, ensure_ascii=False)
        else:
            return json.dumps({"success": True, "message": "No se requirieron cambios técnicos."}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"Error al procesar información de ciudad: {str(e)}"})