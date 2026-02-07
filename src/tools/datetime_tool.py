# tools/datetime_tool.py

from datetime import datetime as dt
from typing import Dict, Any
# Importamos pytz ya que el código lo usa (aunque estaba comentado en el original, estaba roto)
import pytz 
from .registry import tool
from src.core.utils import debug_print

# Definición de la herramienta
DATETIME_TOOL_SCHEMA = {
    "description": "Obtiene la fecha y hora actual. Úsala cuando el usuario pregunte por la hora, fecha, día, mes, año o zona horaria actual. Puede formatear la salida según sea necesario. También útil para verificar fechas de cumpleaños o eventos.",
    "parameters": {
        "type": "object",
        "properties": {
            "timezone": {
                "type": "string",
                "description": "Zona horaria en formato IANA (ej. 'America/Bogota') o nombre común. Si no se especifica, se usa UTC. Nombres comunes aceptados: bogota, colombia, cali, mexico, argentina, chile, peru, espana, usa, ny, la, utc, gmt."
            },
            "format": {
                "type": "string",
                "description": "Formato de salida deseado. Opciones: 'full' (día completo, fecha y hora), 'date' (solo fecha), 'time' (solo hora), 'day' (solo día de la semana), 'iso' (formato ISO 8601), 'custom' (usa patrón personalizado). Por defecto: 'full'",
                "enum": ["full", "date", "time", "day", "iso", "custom"]
            },
            "format_pattern": {
                "type": "string",
                "description": "Patrón personalizado para formatear la fecha/hora (solo si format='custom'). Usa códigos strftime de Python. Ejemplos: '%Y-%m-d %H:%M:%S', '%A %d de %B del %Y'"
            },
            "language": {
                "type": "string",
                "description": "Idioma para los nombres de días/meses. Opciones: 'es' (español), 'en' (inglés). Por defecto: 'es'",
                "enum": ["es", "en"]
            }
        },
        "required": []  # Todos los parámetros son opcionales
    }
}

@tool(schema=DATETIME_TOOL_SCHEMA)
def datetime(timezone: str = "UTC", format: str = "full", 
             format_pattern: str = "", language: str = "es", **kwargs) -> Dict[str, Any]:
    """
    Herramienta para obtener información de fecha y hora actual.
    
    Args:
        timezone: Zona horaria (IANA o nombre común)
        format: Formato de salida
        format_pattern: Patrón personalizado si format='custom'
        language: Idioma para nombres (es/en)
    
    Returns:
        Diccionario con información estructurada de fecha/hora
    """
    debug_print("  [TOOL] Herramienta llamada: datetime")
    
    try:
        # Mapeo de nombres comunes a zonas IANA
        common_timezones = {
            'bogota': 'America/Bogota',
            'colombia': 'America/Bogota',
            'cali': 'America/Bogota',
            'mexico': 'America/Mexico_City',
            'argentina': 'America/Argentina/Buenos_Aires',
            'chile': 'America/Santiago',
            'peru': 'America/Lima',
            'espana': 'Europe/Madrid',
            'usa': 'America/New_York',
            'ny': 'America/New_York',
            'la': 'America/Los_Angeles',
            'utc': 'UTC',
            'gmt': 'UTC'
        }
        
        # Determinar zona horaria
        tz_lower = timezone.lower().strip() if timezone else "utc"
        tz_str = common_timezones.get(tz_lower, timezone if timezone else "UTC")
        
        # Validar y obtener zona horaria
        try:
            tz = pytz.timezone(tz_str)
        except pytz.exceptions.UnknownTimeZoneError:
            # Fallback a UTC
            print(f"  ⚠️ Zona horaria '{timezone}' no reconocida. Usando UTC.")
            tz = pytz.UTC
            tz_str = "UTC"
        except AttributeError:
             # Si pytz no tiene .exceptions, se asume que no está instalado
             raise ImportError("pytz")
        
        # Obtener fecha/hora actual
        current_time = dt.now(tz)
        
        # Diccionarios para traducción
        month_names_es = {
            1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
            5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
            9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
        }
        
        weekday_names_es = {
            0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
            4: "viernes", 5: "sábado", 6: "domingo"
        }
        
        month_names_en = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }
        
        weekday_names_en = {
            0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
            4: "Friday", 5: "Saturday", 6: "Sunday"
        }
        
        # Seleccionar diccionarios según idioma
        month_names = month_names_es if language == 'es' else month_names_en
        weekday_names = weekday_names_es if language == 'es' else weekday_names_en
        
        # Formatear según el tipo solicitado
        if format == 'iso':
            formatted = current_time.isoformat()
        elif format == 'date':
            if language == 'es':
                formatted = f"{current_time.day} de {month_names[current_time.month]} de {current_time.year}"
            else:
                formatted = current_time.strftime("%B %d, %Y")
        elif format == 'time':
            formatted = current_time.strftime("%H:%M:%S")
        elif format == 'day':
            weekday = weekday_names[current_time.weekday()]
            if language == 'es':
                formatted = f"Hoy es {weekday}"
            else:
                formatted = f"Today is {weekday}"
        elif format == 'custom' and format_pattern:
            formatted = current_time.strftime(format_pattern)
        else:  # 'full' por defecto
            if language == 'es':
                weekday = weekday_names[current_time.weekday()].capitalize()
                month = month_names[current_time.month]
                formatted = (f"{weekday}, {current_time.day} de {month} de {current_time.year}, "
                           f"{current_time.hour:02d}:{current_time.minute:02d}:{current_time.second:02d} ({current_time.tzname()})")
            else:
                formatted = current_time.strftime("%A, %B %d, %Y, %H:%M:%S (%Z)")
        
        # Descripción legible según idioma
        hour = current_time.hour
        if language == 'es':
            time_of_day = "de la madrugada" if hour < 6 else \
                         "de la mañana" if hour < 12 else \
                         "de la tarde" if hour < 19 else \
                         "de la noche"
            human_readable = f"Son las {current_time.hour:02d}:{current_time.minute:02d}:{current_time.second:02d} {time_of_day}"
        else:
            time_of_day = "AM" if hour < 12 else "PM"
            hour_12 = hour if hour <= 12 else hour - 12
            if hour_12 == 0:
                hour_12 = 12
            human_readable = f"It's {hour_12}:{current_time.minute:02d}:{current_time.second:02d} {time_of_day}"
        
        # Retornar respuesta estructurada
        return {
            "success": True,
            "datetime_info": {
                "formatted": formatted,
                "iso_format": current_time.isoformat(),
                "timezone": tz_str,
                "utc_offset": current_time.strftime("%z"),
                "timestamp": current_time.timestamp()
            },
            "components": {
                "year": current_time.year,
                "month": current_time.month,
                "day": current_time.day,
                "weekday": weekday_names[current_time.weekday()] if language == 'es' else current_time.strftime("%A"),
                "hour": current_time.hour,
                "minute": current_time.minute,
                "second": current_time.second
            },
            "human_readable": human_readable,
            "timezone_used": tz_str
        }
        
    except ImportError:
         return {
            "success": False,
            "error": "Error: La librería 'pytz' no está instalada, no se puede obtener la hora con zona horaria."
         }
    except Exception as e:
        print(f"  ❌ Error en datetime: {str(e)}")
        return {
            "success": False,
            "error": f"Error al obtener la fecha/hora: {str(e)}",
            "suggestion": "Usa una zona horaria válida como 'America/Bogota' o 'UTC'"
        }
