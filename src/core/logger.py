"""
Módulo de logging seguro para compatibilidad Windows/Linux.
Reemplaza emojis por texto plano cuando la consola no soporta Unicode.
"""
import sys

# Detectar si la consola soporta Unicode
UNICODE_SAFE = (
    sys.stdout.encoding
    and sys.stdout.encoding.lower() in ('utf-8', 'utf8')
)

# Mapeo emoji → texto plano para Windows
EMOJI_MAP = {
    "✅": "[OK]",
    "❌": "[ERROR]",
    "⚠️": "[WARN]",
    "🛑": "[STOP]",
    "🧪": "[TEST]",
    "⏳": "[WAIT]",
    "📌": "[NOTE]",
    "🎉": "[DONE]",
    "🛠️": "[TOOL]",
    "🛡️": "[SHIELD]",
    "ℹ️": "[INFO]",
    "📡": "[API]",
    "💡": "[HINT]",
    "📄": "[DOC]",
    "🧠": "[THINKING]",
    "📝": "[LOG]",
    "🚀": "[LAUNCH]",
    "✨": "[DONE]",
}


def safe_print(*args, **kwargs):
    """print() wrapper que reemplaza emojis automáticamente en Windows."""
    if UNICODE_SAFE:
        print(*args, **kwargs)
    else:
        text = " ".join(str(a) for a in args)
        for emoji, replacement in EMOJI_MAP.items():
            text = text.replace(emoji, replacement)
        print(text, **kwargs)
