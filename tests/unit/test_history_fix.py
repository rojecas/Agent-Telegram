from src.core.history_manager import HistoryManager
import os
import json

class MockMessage:
    def __init__(self, role, content):
        self.role = role
        self.content = content

def test_history():
    chat_id = "test_persistence_123"
    messages = [
        {"role": "user", "content": "Hola Andrew"},
        MockMessage("assistant", "Hola! Soy Andrew. ¿En qué puedo ayudarte?"),
        {"role": "user", "content": "Dime la hora"},
        MockMessage("assistant", "Son las 10:00 PM.")
    ]
    
    print("Saving test history...")
    HistoryManager.save_history(chat_id, messages)
    
    path = HistoryManager._get_path(chat_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            saved = json.load(f)
            print(f"Saved content: {json.dumps(saved, indent=2)}")
            if len(saved) == 4:
                print("✅ Success: All 4 messages saved.")
            else:
                print(f"❌ Error: Only {len(saved)} messages saved.")
    else:
        print("❌ Error: History file not created.")
    
    # Cleanup
    if os.path.exists(path):
        os.remove(path)

if __name__ == "__main__":
    test_history()
