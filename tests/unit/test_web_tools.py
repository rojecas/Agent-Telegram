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

if __name__ == '__main__':
    try:
        test_import_and_registration()
        test_web_search_returns_json()
        test_read_url_returns_json()
        print("\nAll web_tools tests passed.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)