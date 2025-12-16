import sys
import time
from threading import Timer
from src.models.DM.dm import DM
from src.models.DM.input import InputLevel, Type
from pathlib import Path
from src.models.Lead import Lead

backend_path = Path(__file__).parent.parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))


"""DMs buffer Of all users writing now"""
DM_Level: dict[str, DM] = {}

"""Active timers for each chat"""
active_timers: dict[str, Timer] = {}

"""Callback function to be set from wait_and_reply"""
timeout_callback = None

TIMEOUT_SECONDS = 10


def set_timeout_callback(callback):
    """Set the callback function that will be called when timeout expires"""
    global timeout_callback
    timeout_callback = callback


def clear_dm(chat_id: str):
    """Clear all messages for a specific chat after processing"""
    if chat_id in DM_Level:
        DM_Level[chat_id] = DM(
            Lead=None,
            dm1='',
            dm2='',
            dm3='',
            dm4='',
            dm5=''
        )
    cancel_timer(chat_id)


def on_timeout_expired(chat_id: str):
    """Called when the timer expires"""
    print(f"⏰ Timeout expired for chat_id: {chat_id} - processing messages now")
    
    dm = DM_Level.get(chat_id)
    if dm and dm.Lead:
        if chat_id in active_timers:
            del active_timers[chat_id]
        
        if timeout_callback:
            timeout_callback(dm.Lead)
            clear_dm(chat_id)


def start_timer(chat_id: str):
    """Start a timer for this chat"""
    if chat_id in active_timers:
        active_timers[chat_id].cancel()
    
    print(f"⏱️ Starting {TIMEOUT_SECONDS}-second timer for chat_id: {chat_id}")
    timer = Timer(TIMEOUT_SECONDS, on_timeout_expired, args=[chat_id])
    timer.start()
    active_timers[chat_id] = timer


def cancel_timer(chat_id: str):
    """Cancel the timer for this chat"""
    if chat_id in active_timers:
        print(f"❌ Cancelling timer for: {chat_id}")
        active_timers[chat_id].cancel()
        del active_timers[chat_id]


def add_input_to_dm(input: InputLevel) -> Lead:
    """
    Add input to DM buffer and check if processing should be triggered.
    Returns Lead only when 5 messages are reached or timer expires.
    """
    print(f"📥 Adding message type: {input.type}")
    dm_exists(input.chat_id)
    
    if input.type == Type.TEXT:
        lead = add_dm_text(input)
        # Check if we should process now
        should_process = check_message_state_text(lead.chat_id)
        if should_process:
            return lead  # Only return when 5 messages reached
        return None  # Otherwise return None, wait for timer
    elif input.type == Type.IMAGE:
        lead = add_dm_image(input)
        should_process = check_message_state_image(lead.chat_id)
        if should_process:
            return lead
        return None
    
    return None


def add_dm_text(input: InputLevel) -> Lead:
    """Add text message to DM buffer"""
    dm = DM_Level.get(input.chat_id)
    if dm.dm1 == '' or dm.dm1 == None:
        dm.dm1 = input.message
    elif dm.dm2 == '' or dm.dm2 == None:
        dm.dm2 = input.message
    elif dm.dm3 == '' or dm.dm3 == None:
        dm.dm3 = input.message
    elif dm.dm4 == '' or dm.dm4 == None:
        dm.dm4 = input.message
    elif dm.dm5 == '' or dm.dm5 == None:
        dm.dm5 = input.message

    message = f"{dm.dm1} {dm.dm2} {dm.dm3} {dm.dm4} {dm.dm5}".strip()

    dm.Lead = Lead(
        chat_id=input.chat_id,
        user_id=input.user_id,
        user=input.user,
        type=input.type,
        message=message,
        image=None,
        audio=None
    )
    return dm.Lead


def add_dm_image(input: InputLevel) -> Lead:
    """Add image message to DM buffer"""
    dm = DM_Level.get(input.chat_id)
    if dm.dm1 == '' or dm.dm1 == None:
        dm.dm1 = input.message
    elif dm.dm2 == '' or dm.dm2 == None:
        dm.dm2 = input.message
    elif dm.dm3 == '' or dm.dm3 == None:
        dm.dm3 = input.message
    elif dm.dm4 == '' or dm.dm4 == None:
        dm.dm4 = input.message
    elif dm.dm5 == '' or dm.dm5 == None:
        dm.dm5 = input.message

    message = f"{dm.dm1} {dm.dm2} {dm.dm3} {dm.dm4} {dm.dm5}".strip()

    dm.Lead = Lead(
        chat_id=input.chat_id,
        user_id=input.user_id,
        user=input.user,
        type=input.type,
        message=message,
        image=input.image,
        audio=None
    ) 
    
    return dm.Lead


def check_message_state_text(chat_id: str) -> bool:
    """
    Check message state and determine if processing should be triggered.
    Returns True only when 5 messages are reached (immediate processing).
    Returns False otherwise (wait for timer).
    """
    dm = DM_Level.get(chat_id)
    if not dm:
        print(f"❌ No DM found for chat_id: {chat_id}")
        return False
    
    print(f"📊 Checking state for chat_id: {chat_id}")
    DM1 = dm.dm1
    DM2 = dm.dm2
    DM3 = dm.dm3
    DM4 = dm.dm4
    DM5 = dm.dm5
    
    # Count non-empty messages
    message_count = sum([
        bool(DM1 and DM1 != ""),
        bool(DM2 and DM2 != ""),
        bool(DM3 and DM3 != ""),
        bool(DM4 and DM4 != ""),
        bool(DM5 and DM5 != "")
    ])
    
    print(f"📝 Message count: {message_count}/5")
    
    # First message: start timer
    if message_count == 1:
        print("✅ First message - starting timer")
        start_timer(chat_id)
        return False  # Don't process yet
    
    # Messages 2-4: just wait
    elif message_count < 5:
        print(f"⏳ Message {message_count} added to batch - waiting...")
        # Timer is already running from first message
        return False  # Don't process yet
    
    # Fifth message: process immediately
    elif message_count == 5:
        print("🎯 5 messages reached - processing immediately!")
        cancel_timer(chat_id)
        return True  # Process now!
    
    return False


def check_message_state_image(chat_id: str) -> bool:
    """
    Check message state for image messages.
    Returns True only when 5 messages are reached (immediate processing).
    Returns False otherwise (wait for timer).
    """
    dm = DM_Level.get(chat_id)
    if not dm:
        print(f"❌ No DM found for chat_id: {chat_id}")
        return False
    
    print(f"📊 Checking image state for chat_id: {chat_id}")
    DM1 = dm.dm1
    DM2 = dm.dm2
    DM3 = dm.dm3
    DM4 = dm.dm4
    DM5 = dm.dm5
    
    # Count non-empty messages
    message_count = sum([
        bool(DM1 and DM1 != ""),
        bool(DM2 and DM2 != ""),
        bool(DM3 and DM3 != ""),
        bool(DM4 and DM4 != ""),
        bool(DM5 and DM5 != "")
    ])
    
    print(f"📝 Image message count: {message_count}/5")
    
    # First message: start timer
    if message_count == 1:
        print("✅ First image message - starting timer")
        start_timer(chat_id)
        return False
    
    # Messages 2-4: just wait
    elif message_count < 5:
        print(f"⏳ Image message {message_count} added - waiting...")
        return False
    
    # Fifth message: process immediately
    elif message_count == 5:
        print("🎯 5 image messages reached - processing immediately!")
        cancel_timer(chat_id)
        return True
    
    return False


def dm_exists(chat_id: str) -> None:
    """Initialize DM buffer if it doesn't exist"""
    if chat_id not in DM_Level:
        DM_Level[chat_id] = DM(
            Lead=None,
            dm1='',
            dm2='',
            dm3='',
            dm4='',
            dm5=''
        )