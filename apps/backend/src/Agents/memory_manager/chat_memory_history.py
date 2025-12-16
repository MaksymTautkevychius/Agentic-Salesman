from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from threading import RLock, Thread
import time,asyncio
from src.database.database import get_messages_by_session_id, add_message as db_add_message
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from typing import List

memory_lock = RLock()
cache_lock = RLock()



memory_cache: Dict[str, dict] = {}


CACHE_TTL_SECONDS = 3600  # 1 hour
MAX_CACHE_SIZE = 100      # Maximum number of sessions to cache
MAX_MESSAGES_PER_SESSION = 40  # database limit

class AIMemoryManager:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self._ensure_session_exists()

    def _ensure_session_exists(self) -> None:
        with cache_lock:
            if self.session_id not in memory_cache:
                memory_cache[self.session_id] = {
                    'messages': [],
                    'last_access': datetime.now(),
                    'dirty': False
                }

    def retrieve_messages(self) -> List[Dict[str, str]]:
        with memory_lock:
            cache_entry = memory_cache[self.session_id]

            if not cache_entry['messages']:
                try:
                    db_messages = get_messages_by_session_id(self.session_id)  # returns [(message_dict,), ...]
                    cache_entry['messages'] = [msg[0] for msg in db_messages]
                except Exception as e:
                    print(f"Error loading messages for {self.session_id}: {e}")
                    cache_entry['messages'] = []

            cache_entry['last_access'] = datetime.now()
            return list(cache_entry['messages'])

    def add_message(self, message_type: str, content: str) -> Optional[int]:
        message = {'type': message_type, 'content': content}

        with memory_lock:
            cache_entry = memory_cache[self.session_id]
            cache_entry['messages'].append(message)
            cache_entry['last_access'] = datetime.now()


            if len(cache_entry['messages']) > MAX_MESSAGES_PER_SESSION:
                cache_entry['messages'] = cache_entry['messages'][-MAX_MESSAGES_PER_SESSION:]

            try:
                message_id = db_add_message(self.session_id, message)
                cache_entry['dirty'] = False
                return message_id
            except Exception as e:
                print(f"Error saving message for {self.session_id}: {e}")
                cache_entry['dirty'] = True
                return None

    def add_messages_batch(self, messages: List[Dict[str, str]]) -> List[Optional[int]]:
        ids: List[Optional[int]] = []
        for msg in messages:
            ids.append(self.add_message(msg['type'], msg['content']))
        return ids

    def get_messages_for_langchain(self) -> List[Tuple[str, str]]:
        messages = self.retrieve_messages()
        return [(m['type'], m['content']) for m in messages]

    def get_human_messages(self) -> List[str]:
        return [m['content'] for m in self.retrieve_messages() if m['type'] == 'human']

    def get_ai_messages(self) -> List[str]:
        return [m['content'] for m in self.retrieve_messages() if m['type'] == 'ai']

    def clear_history(self) -> None:
        with memory_lock:
            if self.session_id in memory_cache:
                memory_cache[self.session_id]['messages'] = []
                memory_cache[self.session_id]['dirty'] = False

    def get_context_window(self, max_messages: int = 10) -> List[Dict[str, str]]:
        messages = self.retrieve_messages()
        return messages[-max_messages:] if len(messages) > max_messages else messages

    def get_conversation_summary(self) -> Dict[str, Any]:
        messages = self.retrieve_messages()
        return {
            'session_id': self.session_id,
            'total_messages': len(messages),
            'human_messages': len([m for m in messages if m['type'] == 'human']),
            'ai_messages': len([m for m in messages if m['type'] == 'ai']),
            'last_message': messages[-1] if messages else None
        }

    def get_formatted_history(self) -> str:
        messages = self.retrieve_messages()
        formatted = []
        for msg in messages:
            role = "Human" if msg['type'] == 'human' else "AI"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted)
    
    def get_conversation_buffer_memory(self):
        history_list = self.get_messages_for_langchain()

        langchain_messages = []
        for role, content in history_list:
            if role == "human":
                langchain_messages.append(HumanMessage(content=content))
            else:
                langchain_messages.append(AIMessage(content=content))

        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            input_key="input",
            output_key="output"
        )

        for message in langchain_messages:
            memory.chat_memory.add_message(message)
        print(memory)
        return memory
    

def cleanup_stale_sessions() -> int:
    with cache_lock:
        current_time = datetime.now()
        to_remove = [
        session_id for session_id, data in memory_cache.items()
        if (current_time - data['last_access']).total_seconds() > CACHE_TTL_SECONDS
        ]
        for session_id in to_remove:
            del memory_cache[session_id]
        print(f"Cleaned up {len(to_remove)} stale sessions")
        return len(to_remove)

def enforce_cache_size_limit() -> int:
    with cache_lock:
        if len(memory_cache) <= MAX_CACHE_SIZE:
            return 0

        sorted_sessions = sorted(
            memory_cache.items(),
            key=lambda x: x[1]['last_access']
        )

        sessions_to_remove = len(memory_cache) - MAX_CACHE_SIZE
        for session_id, _ in sorted_sessions[:sessions_to_remove]:
            del memory_cache[session_id]

        print(f"Removed {sessions_to_remove} sessions to enforce cache limit")
        return sessions_to_remove


def get_all_active_sessions() -> List[str]:
    with cache_lock:
        return list(memory_cache.keys())


def get_cache_stats() -> Dict[str, Any]:
    with cache_lock:
        total_messages = sum(len(data['messages']) for data in memory_cache.values())
        dirty_count = sum(1 for data in memory_cache.values() if data['dirty'])

        return {
            'active_sessions': len(memory_cache),
            'total_cached_messages': total_messages,
            'dirty_sessions': dirty_count,
            'cache_limit': MAX_CACHE_SIZE,
            'ttl_seconds': CACHE_TTL_SECONDS
        }


def sync_dirty_sessions() -> int:
    synced = 0
    with memory_lock:
        for session_id, data in memory_cache.items():
            if data['dirty'] and data['messages']:
                last_msg = data['messages'][-1]
                try:
                    db_add_message(session_id, last_msg)
                    data['dirty'] = False
                    synced += 1
                except Exception:
                    # Keep clean, gives error
                    pass

    if synced > 0:
        print(f"Synced {synced} dirty sessions to database")
    return synced


def cache_maintenance_task():
    while True:
        try:
            time.sleep(300)  
            cleanup_stale_sessions()
            enforce_cache_size_limit()
            sync_dirty_sessions()
            print(f"Cache stats: {get_cache_stats()}")
        except Exception as e:
            print(f"Error in cache maintenance: {e}")


def start_cache_maintenance_thread() -> Thread:
    t = Thread(target=cache_maintenance_task, daemon=True)
    t.start()
    return t


def example_usage():
    print("inside example_usage")
    chat_id = "123456789"
    manager = AIMemoryManager(chat_id)

    manager.add_message("human", "Hello, AI!")
    manager.add_message("ai", "Hello! How can I help you today?")

    messages = manager.retrieve_messages()
    print(f"Total messages: {len(messages)}")
    for msg in messages:
        print(f"  {msg['type']}: {msg['content']}")

    human_msgs = manager.get_human_messages()
    print(f"\nHuman messages: {human_msgs}")

    context = manager.get_context_window(max_messages=5)
    print(f"\nContext window (last 5): {context}") 

    formatted = manager.get_formatted_history()
    print(f"\nFormatted history:\n{formatted}")

    summary = manager.get_conversation_summary()
    print(f"\nConversation summary: {summary}")