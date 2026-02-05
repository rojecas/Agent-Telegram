from src.agent_telegram.tools.registry import tool_registry
import src.agent_telegram.tools.city_tools
import os
import json

def test_city_optimization():
    print("🚀 Probando optimización de City Tools...")
    
    city_name = "pereira_test"
    file_path = f"./assets/cities/{city_name}.ledger"
    
    # Asegurar que no exista antes de la prueba
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # 1. Probar add_city_info para una ciudad inexistente
    add_city_tool = tool_registry.get_tool_call_map()["add_city_info"]
    
    info_to_add = {
        "parques_y_naturaleza": [
            {"nombre": "Parque Olaya Herrera", "descripcion": "Parque principal de la ciudad de Pereira."}
        ],
        "experiencias_gastronomicas": [
            {"nombre": "Lucerna", "descripcion": "Famosa pastelería y heladería tradicional."}
        ]
    }
    
    print(f"--- Intentando crear ciudad: {city_name} ---")
    result_str = add_city_tool(city=city_name, info_json=json.dumps(info_to_add))
    result = json.loads(result_str)
    
    if result.get("success"):
        print("✅ Herramienta reportó éxito.")
    else:
        print(f"❌ Error reportado por la herramienta: {result.get('error')}")
        return

    # 2. Verificar existencia del archivo y estructura
    if os.path.exists(file_path):
        print(f"✅ Archivo {file_path} creado exitosamente.")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        city_key = city_name
        if city_key in data:
            print(f"✅ Estructura base '{city_key}' encontrada.")
            categories = list(data[city_key].keys())
            print(f"Categorías creadas: {categories}")
            
            # Verificar una categoría esperada del template
            if "atractivos_culturales" in categories:
                print("✅ Categoría del template 'atractivos_culturales' presente (aunque esté vacía).")
            else:
                print("❌ Falta categoría del template 'atractivos_culturales'.")
                
            # Verificar datos insertados
            parques = data[city_key].get("parques_y_naturaleza", [])
            if any(p["nombre"] == "Parque Olaya Herrera" for p in parques):
                print("✅ Datos insertados correctamente.")
            else:
                print("❌ Datos no encontrados en el archivo.")
        else:
            print(f"❌ La llave raíz '{city_key}' no se encontró en el archivo.")
    else:
        print(f"❌ El archivo {file_path} NO fue creado.")

    # Limpieza
    if os.path.exists(file_path):
        os.remove(file_path)

if __name__ == "__main__":
    test_city_optimization()
