import pytest
from unittest.mock import patch, MagicMock
from agents import send_response
from models import Message

@patch("builtins.print")
def test_send_response_keyboard(mock_print):
    # Context with source='keyboard'
    context = Message(priority=2, content="hi", source="keyboard", user_id="1", chat_id="1")
    
    send_response("Hello Keyboard", context)
    
    # Should print to console
    mock_print.assert_called()
    args, _ = mock_print.call_args
    assert "Hello Keyboard" in args[0]
    assert "[🤖 Andrew]" in args[0]

@patch("tools.telegram_tool.telegram_send")
def test_send_response_telegram(mock_tg_send):
    # Context with source='telegram'
    context = Message(priority=2, content="hi", source="telegram", user_id="1", chat_id="12345")
    
    send_response("Hello Telegram", context)
    
    # Should call telegram_send
    mock_tg_send.assert_called_once_with(text="Hello Telegram", chat_id="12345", parse_mode="HTML")

@patch("builtins.print")
def test_send_response_none_context(mock_print):
    # No context (default to keyboard)
    send_response("Default msg", None)
    
    mock_print.assert_called()
    assert "Default msg" in mock_print.call_args[0][0]
