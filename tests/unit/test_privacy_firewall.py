import pytest
import json
from unittest.mock import patch, mock_open
from src.tools.user_tools import read_ledger
from src.core.models import Message

# Mock ledger data
MOCK_LEDGER = {
    "public_profile": {
        "name": "Test User",
        "location": "Cali"
    },
    "private_profile": {
        "secret": "12345",
        "age": 25
    }
}

@pytest.fixture
def mock_ledger_file():
    with patch("builtins.open", mock_open(read_data=json.dumps(MOCK_LEDGER))):
        with patch("os.path.exists", return_value=True):
            yield

def test_read_ledger_group_context_blocks_private(mock_ledger_file):
    # Mock context as a group
    context = Message(priority=2, content="hi", source="telegram", user_id="1", chat_id="-100") # Negative chat_id = Group
    
    # Even if we request PRIVATE with the correct secret, it should be blocked
    result_json = read_ledger(user="test.user", secret_attempt="12345", scope="PRIVATE", context=context)
    result = json.loads(result_json)
    
    assert result["authorized"] == True
    assert result["scope_delivered"] == "PUBLIC"
    assert "age" not in result["profile"]
    assert result["profile"]["location"] == "Cali"

def test_read_ledger_dm_context_allows_private(mock_ledger_file):
    # Mock context as a private chat (DM)
    context = Message(priority=2, content="hi", source="telegram", user_id="1", chat_id="1") 
    
    # Should allow PRIVATE access with correct secret
    result_json = read_ledger(user="test.user", secret_attempt="12345", scope="PRIVATE", context=context)
    result = json.loads(result_json)
    
    assert result["authorized"] == True
    assert result["scope_delivered"] == "PRIVATE"
    assert result["profile"]["private_profile"]["age"] == 25

def test_read_ledger_dm_context_denies_wrong_secret(mock_ledger_file):
    # Mock context as a private chat (DM)
    context = Message(priority=2, content="hi", source="telegram", user_id="1", chat_id="1") 
    
    # Should deny PRIVATE access with wrong secret
    result_json = read_ledger(user="test.user", secret_attempt="WRONG", scope="PRIVATE", context=context)
    result = json.loads(result_json)
    
    assert result["authorized"] == False
    assert "error" in result
