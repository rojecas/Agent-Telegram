import pytest
from src.core.telegram_utils import escape_html_for_telegram, chunk_telegram_message

class TestTelegramUtils:

    def test_escape_html_respects_allowed_tags(self):
        """Verifica que las etiquetas HTML válidas de Telegram NO se escapen."""
        text = "This is <b>bold</b> and <i>italic</i> and <code>code</code>."
        escaped = escape_html_for_telegram(text)
        assert escaped == text

    def test_escape_html_handles_invalid_brackets(self):
        """Verifica que los `<` y `>` que no formen etiquetas HTML válidas se escapen."""
        text = "El costo fue <$20,000> y <10."
        escaped = escape_html_for_telegram(text)
        assert escaped == "El costo fue &lt;$20,000&gt; y &lt;10."

    def test_escape_html_mixed_content(self):
        """Verifica que se mezclen correctamente etiquetas válidas y brackets a escapar."""
        text = "Este es un <b>costo</b> de <$20,000 y <i>puede causar errores</i> >."
        escaped = escape_html_for_telegram(text)
        assert escaped == "Este es un <b>costo</b> de &lt;$20,000 y <i>puede causar errores</i> &gt;."

    def test_escape_html_empty_string(self):
        """Verifica el manejo de strings vacíos o None."""
        assert escape_html_for_telegram("") == ""
        assert escape_html_for_telegram(None) == ""

    def test_chunk_message_short(self):
        """Verifica que un mensaje corto no se divida."""
        text = "Hola mundo"
        chunks = chunk_telegram_message(text, max_length=50)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_message_long_with_newlines(self):
        """Verifica la división respetando los saltos de línea."""
        base = "Línea " + "A" * 10
        # Construimos un string de 3 líneas
        text = f"{base}\n{base}\n{base}"
        
        # Con max_length justo para albergar 1 línea (con len() ~= 16)
        # Forzamos que max_length=20 pueda contener una sola línea (Línea AAAAAAAAAA)
        chunks = chunk_telegram_message(text, max_length=20)
        
        assert len(chunks) == 3
        # Validamos que se hicieron cortes limpios en los \n
        assert chunks[0] == base
        assert chunks[1] == base
        assert chunks[2] == base

    def test_chunk_message_long_with_spaces(self):
        """Verifica la división por espacios cuando no hay saltos de línea."""
        text = "A" * 20 + " " + "B" * 20
        # max_length=30 hará que el corte sea en el espacio (' ')
        chunks = chunk_telegram_message(text, max_length=30)
        
        assert len(chunks) == 2
        assert chunks[0] == "A" * 20
        assert chunks[1] == "B" * 20

    def test_chunk_message_long_no_spaces(self):
        """Verifica el corte forzado (truncado exacto) cuando no hay espacios ni saltos de línea."""
        text = "A" * 50
        chunks = chunk_telegram_message(text, max_length=20)
        
        assert len(chunks) == 3
        assert chunks[0] == "A" * 20
        assert chunks[1] == "A" * 20
        assert chunks[2] == "A" * 10

    def test_chunk_empty_string(self):
        """Verifica el manejo de strings nulos o vacíos en el chunker."""
        assert chunk_telegram_message("") == []
        assert chunk_telegram_message(None) == []
