# tools/city_tools.py

import os
import json
from typing import Dict, Any, List
from tools.registry import tool

# --- Herramienta: Leer información de ciudad (read_city_info) ---
READ_CITY_INFO_SCHEMA = {
    "description": "Obtiene información detallada sobre una ciudad específica (Cali, Bogota, Medellin, Barranquilla) leyendo su archivo ledger correspondiente.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "El nombre de la ciudad a consultar (ej: 'cali', 'bogota')"
            }
        },
        "required": ["city"]
    }
}

@tool(schema=READ_CITY_INFO_SCHEMA)
def read_city_info(city: str) -> str:
    print(f"  ⚙️ Herramienta llamada: read_city_info ({city})")
    try:
        city_lower = city.lower().strip()
        file_path = f"./assets/cities/{city_lower}.ledger"
        
        if not os.path.exists(file_path):
            return json.dumps({"error": f"No se encontró información para la ciudad: {city}"})
            
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        return json.dumps(data, indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        return json.dumps({"error": f"Error: El archivo de datos de {city} está corrupto."})
    except Exception as e:
        return json.dumps({"error": f"Error al leer información de ciudad: {str(e)}"})

# --- Herramienta: Agregar información a ciudad (add_city_info) ---
ADD_CITY_INFO_SCHEMA = {
    "description": "Agrega o actualiza información en el archivo de una ciudad. Recibe el nombre de la ciudad y un JSON con las categorías y elementos a agregar. Si el elemento ya existe (mismo nombre), intenta actualizarlo o agregar items a sus listas.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "Nombre de la ciudad (ej: 'cali', 'bogota')"
            },
            "info_json": {
                "type": "string",
                "description": "JSON String con la estructura {'categoria': [{'nombre': '...', ...}]}"
            }
        },
        "required": ["city", "info_json"]
    }
}

@tool(schema=ADD_CITY_INFO_SCHEMA)
def add_city_info(city: str, info_json: str) -> str:
    print(f"  ⚙️ Herramienta llamada: add_city_info ({city})")
    try:
        city_lower = city.lower().strip()
        file_path = f"./assets/cities/{city_lower}.ledger"
        
        if not os.path.exists(file_path):
            return json.dumps({"error": f"No se encontró información para la ciudad: {city}"})
            
        try:
            new_info = json.loads(info_json)
        except json.JSONDecodeError:
            return json.dumps({"error": "El argumento info_json no es un JSON válido."})

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Buscar la estructura correcta de la ciudad
        city_data = data.get(city_lower, {})
        # Fallback: si no encuentra la llave por nombre, usa el primer valor (ej: "cali" en cali.ledger)
        if not city_data:
             if len(data) == 1:
                 city_key = list(data.keys())[0]
                 city_data = data[city_key]
             else:
                 city_data = data # Asumir estructura plana o mixta si falla lo anterior

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
                
                # Check for existing item
                existing_item = next((item for item in city_data[category] if isinstance(item, dict) and item.get("nombre") == new_item["nombre"]), None)
                
                if existing_item:
                    # Update logic
                    updated_fields = []
                    for key, value in new_item.items():
                        if key == "nombre": continue
                        
                        # Si ambos son listas, intentamos hacer append de los elementos nuevos
                        if isinstance(value, list) and isinstance(existing_item.get(key), list):
                             for v in value:
                                 if v not in existing_item[key]:
                                     existing_item[key].append(v)
                                     updated_fields.append(f"{key} (item added)")
                        # Si no son listas, actualizamos el valor si es diferente
                        elif existing_item.get(key) != value:
                             existing_item[key] = value
                             updated_fields.append(key)
                    
                    if updated_fields:
                        messages.append(f"🔄 Actualizado '{new_item['nombre']}' en '{category}': {', '.join(updated_fields)}")
                        changes_made = True
                    else:
                        messages.append(f"ℹ️ '{new_item['nombre']}' ya existe en '{category}' y no requiere cambios.")
                        
                else:
                    # Add new item
                    city_data[category].append(new_item)
                    messages.append(f"✅ Agregado '{new_item['nombre']}' a '{category}'.")
                    changes_made = True

        if changes_made:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return json.dumps({"success": True, "details": messages}, ensure_ascii=False)
        else:
            return json.dumps({"success": True, "message": "No se realizaron cambios nuevos.", "details": messages}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"Error al actualizar información de ciudad: {str(e)}"})