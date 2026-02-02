from tools import add_city_info, read_city_info
import json

city = 'cali'

print(f"--- 1. Testing Add New Item to {city} ---")
new_item = {
    "experiencias_gastronomicas": [
        {
            "nombre": "Prueba Restaurante",
            "descripcion": "Restaurante de prueba pa verificar la tool",
            "ubicacion": "San Fernando",
            "horario": "12:00-22:00",
            "costo_entrada": "Consumo"
        }
    ]
}
result = add_city_info(city, json.dumps(new_item))
print(f"Result Add New: {result}")

print(f"\n--- 2. Testing Update Existing Item (Simple Field) ---")
update_item = {
    "experiencias_gastronomicas": [
        {
            "nombre": "Prueba Restaurante",
            "descripcion": "Restaurante de prueba ACTUALIZADO",
        }
    ]
}
result = add_city_info(city, json.dumps(update_item))
print(f"Result Update Simple: {result}")

print(f"\n--- 3. Testing Update Existing Item (List Append) ---")
# First ensure the item has a list
prep_item = {
    "experiencias_gastronomicas": [
        {
            "nombre": "Prueba Restaurante",
            "platos_recomendados": ["Sancocho"]
        }
    ]
}
add_city_info(city, json.dumps(prep_item))

# Now append
append_item = {
    "experiencias_gastronomicas": [
        {
            "nombre": "Prueba Restaurante",
            "platos_recomendados": ["Chuleta", "Sancocho"] # "Sancocho" shouldn't be dupe-added
        }
    ]
}
result = add_city_info(city, json.dumps(append_item))
print(f"Result Update List: {result}")

print(f"\n--- 4. Verify Final State ---")
final_data = read_city_info(city)
data = json.loads(final_data)
# Find our item
items = data.get('cali', {}).get('experiencias_gastronomicas', [])
target = next((i for i in items if i['nombre'] == "Prueba Restaurante"), None)
print(f"Final Item State: {json.dumps(target, indent=2, ensure_ascii=False)}")
