#!/usr/bin/env python3
"""
Test for web browsing tools (web_search, read_url).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_import_and_registration():
    """Verify that web_tools module can be imported and tools are registered."""
    from src.tools.registry import tool_registry
    import src.tools.web_tools  # noqa: F401

    tool_list = tool_registry.get_tool_list()
    tool_map = tool_registry.get_tool_call_map()

    # Ensure at least the two new tools are present
    tool_names = {schema['function']['name'] for schema in tool_list}
    assert 'web_search' in tool_names, "web_search not found in tool list"
    assert 'read_url' in tool_names, "read_url not found in tool list"

    # Ensure functions are callable
    assert 'web_search' in tool_map
    assert 'read_url' in tool_map

    print("✅ web_tools registration test passed")
    return True

def test_web_search_returns_json():
    """Test that web_search returns a valid JSON string (even if error due to missing deps)."""
    from src.tools.web_tools import web_search
    import json
    result = web_search("test query")
    # Should be a JSON string
    parsed = json.loads(result)
    assert isinstance(parsed, dict)
    # Either contains 'results' or 'error'
    assert 'results' in parsed or 'error' in parsed
    print("✅ web_search returns valid JSON")

def test_read_url_returns_json():
    """Test that read_url returns a valid JSON string."""
    from src.tools.web_tools import read_url
    import json
    result = read_url("https://example.com")
    parsed = json.loads(result)
    assert isinstance(parsed, dict)
    assert 'url' in parsed or 'error' in parsed
    print("✅ read_url returns valid JSON")

def test_telegram_send_document_registration():
    """Test that telegram_send_document is registered and returns valid JSON."""
    from src.tools.registry import tool_registry
    import src.tools.web_tools  # noqa: F401
    
    tool_list = tool_registry.get_tool_list()
    tool_map = tool_registry.get_tool_call_map()
    
    # Ensure telegram_send_document is present
    tool_names = {schema['function']['name'] for schema in tool_list}
    assert 'telegram_send_document' in tool_names, "telegram_send_document not found in tool list"
    assert 'telegram_send_document' in tool_map
    
    # Test function signature
    from src.tools.web_tools import telegram_send_document
    import json
    
    # Test with missing token (should return error JSON)
    result = telegram_send_document("test.pdf")
    parsed = json.loads(result)
    assert isinstance(parsed, dict)
    assert 'error' in parsed or 'success' in parsed
    
    print("✅ telegram_send_document registration test passed")

def test_telegram_send_document_with_mock():
    """Test telegram_send_document with mocked API response."""
    import os
    import json
    import tempfile
    from unittest.mock import patch, mock_open
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test content")
        temp_file = f.name
    
    try:
        # Mock environment variables
        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'test_token', 'TELEGRAM_CHAT_ID': '12345'}):
            # Mock requests.post to simulate Telegram API response
            with patch('src.tools.web_tools.requests.post') as mock_post:
                # Setup mock response
                mock_response = type('MockResponse', (), {})()
                mock_response.json = lambda: {
                    "ok": True,
                    "result": {
                        "message_id": 100,
                        "chat": {"id": 12345},
                        "document": {"file_name": "test.txt"}
                    }
                }
                mock_response.ok = True
                mock_post.return_value = mock_response
                
                # Import after mocking
                from src.tools.web_tools import telegram_send_document
                
                # Test sending local file
                result = telegram_send_document(temp_file, caption="Test document")
                parsed = json.loads(result)
                
                assert parsed['success'] == True
                assert parsed['message_id'] == 100
                assert parsed['chat_id'] == 12345
                
                # Verify API was called
                assert mock_post.called
                
                print("✅ telegram_send_document with mock test passed")
    
    finally:
        # Clean up temp file
        if os.path.exists(temp_file):
            os.unlink(temp_file)

if __name__ == '__main__':
    try:
        test_import_and_registration()
        test_web_search_returns_json()
        test_read_url_returns_json()
        test_telegram_send_document_registration()
        test_telegram_send_document_with_mock()
        print("\nAll web_tools tests passed.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)