import pytest
import queue
from src.agent_telegram.core.models import Message
from datetime import datetime

def test_message_priority_ordering():
    # Priority 1 (System) should be "less than" Priority 2 (User) 
    # so it comes out first in a PriorityQueue.
    msg_system = Message(priority=1, content="System Task", source="system", user_id="sys", chat_id="sys")
    msg_user = Message(priority=2, content="User Task", source="keyboard", user_id="user", chat_id="chat")
    
    assert msg_system < msg_user

def test_priority_queue_retrieval():
    pq = queue.PriorityQueue()
    
    msg_low = Message(priority=2, content="Low Priority", source="keyboard", user_id="u1", chat_id="c1")
    msg_high = Message(priority=1, content="High Priority", source="system", user_id="sys", chat_id="sys")
    
    pq.put(msg_low)
    pq.put(msg_high)
    
    # High priority (1) should come out first
    first = pq.get()
    second = pq.get()
    
    assert first.priority == 1
    assert second.priority == 2
    assert first.content == "High Priority"

def test_message_is_group_logic():
    # Negative ID (Telegram convention)
    msg_group_tg = Message(priority=2, content="Hi", source="telegram", user_id="123", chat_id="-456")
    # Prefix 'grp_' (Custom convention)
    msg_group_custom = Message(priority=2, content="Hi", source="keyboard", user_id="123", chat_id="grp_abc")
    # Positive ID (Private)
    msg_private = Message(priority=2, content="Hi", source="telegram", user_id="123", chat_id="123")
    
    assert msg_group_tg.is_group() == True
    assert msg_group_custom.is_group() == True
    assert msg_private.is_group() == False
