
import re

TELEGRAM_MAX_MESSAGE_LENGTH = 4096

def escape_html_for_telegram(text: str) -> str:
    """
    Escapa caracteres HTML inválidos (<, >) para evitar errores 400 en Telegram
    cuando se usa parse_mode='HTML', respetando las etiquetas válidas permitidas.
    """
    if not text:
        return ""
        
    allowed_tags = ['b', 'strong', 'i', 'em', 'u', 'ins', 's', 'strike', 'del', 'a', 'code', 'pre']
    
    # Expresión regular para coincidir con cualquier estructura que parezca una etiqueta HTML
    pattern = re.compile(r'(</?[a-zA-Z0-9]+[^>]*>)')
    
    # Al usar capture groups () en split, las coincidencias se devuelven intercaladas con el texto
    # Ej: "hola <b>mundo</b>!" -> ["hola ", "<b>", "mundo", "</b>", "!"]
    parts = pattern.split(text)
    
    for i in range(len(parts)):
        # Índices impares son las posibles etiquetas encontradas por la regex
        if i % 2 == 1:
            tag_name_match = re.match(r'</?([a-zA-Z0-9]+)', parts[i])
            if tag_name_match and tag_name_match.group(1).lower() in allowed_tags:
                # Es una etiqueta permitida, la dejamos intacta
                continue
            else:
                # Parecía una etiqueta pero no es válida, la escapamos completa
                parts[i] = parts[i].replace('<', '&lt;').replace('>', '&gt;')
        else:
            # Índices pares son texto normal fuera de cualquier cosa que parezca una etiqueta.
            # Los escapamos ciegamente.
            parts[i] = parts[i].replace('<', '&lt;').replace('>', '&gt;')
            
    return "".join(parts)


def chunk_telegram_message(text: str, max_length: int = TELEGRAM_MAX_MESSAGE_LENGTH) -> list[str]:
    """
    Divide un mensaje largo en múltiples partes asegurando que ninguna exceda `max_length`.
    Intenta dividir por saltos de línea para preservar el formato.
    """
    if not text:
        return []
        
    if len(text) <= max_length:
        return [text]
        
    chunks = []
    current_text = text
    
    while len(current_text) > max_length:
        # Buscar el último salto de línea dentro del límite
        split_index = current_text.rfind('\n', 0, max_length)
        
        # Si no hay saltos de línea, buscar el último espacio
        if split_index == -1:
            split_index = current_text.rfind(' ', 0, max_length)
            
        # Si tampoco hay espacios (una sola palabra gigante), cortar exactamente en el límite
        if split_index == -1:
            split_index = max_length
            
        chunk = current_text[:split_index].strip()
        if chunk:
            chunks.append(chunk)
            
        current_text = current_text[split_index:].strip()
        
    if current_text:
        chunks.append(current_text)
        
    return chunks
