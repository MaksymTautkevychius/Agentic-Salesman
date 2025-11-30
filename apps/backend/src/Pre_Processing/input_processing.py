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

TIMEOUT_SECONDS = 30


def set_timeout_callback(callback):
    """Set the callback function that will be called when timeout expires"""
    global timeout_callback
    timeout_callback = callback


def clear_dm(chat_id: str):
    """Clear all messages for a specific chat after processing"""
    print(f"🧹 Clearing DM for chat_id: {chat_id}")
    if chat_id in DM_Level:
        DM_Level[chat_id] = DM(
            Lead=None,
            dm1='',
            dm2='',
            dm3='',
            dm4='',
            dm5=''
        )
    # Also cancel any active timer
    cancel_timer(chat_id)


def on_timeout_expired(chat_id: str):
    """Called when the 30-second timer expires"""
    print(f"⏰ Timeout expired for chat_id: {chat_id} - processing messages now")
    
    dm = DM_Level.get(chat_id)
    if dm and dm.Lead:
        # Clear the timer reference
        if chat_id in active_timers:
            del active_timers[chat_id]
        
        # Trigger processing via callback
        if timeout_callback:
            timeout_callback(dm.Lead)
            # Clear the DM after processing
            clear_dm(chat_id)


def start_timer(chat_id: str):
    """Start a 30-second timer for this chat"""
    # Cancel existing timer if any
    if chat_id in active_timers:
        active_timers[chat_id].cancel()
    
    # Start new timer
    print(f"⏱️ Starting 30-second timer for chat_id: {chat_id}")
    timer = Timer(TIMEOUT_SECONDS, on_timeout_expired, args=[chat_id])
    timer.start()
    active_timers[chat_id] = timer


def cancel_timer(chat_id: str):
    """Cancel the timer for this chat"""
    if chat_id in active_timers:
        print(f"🛑 Cancelling timer for chat_id: {chat_id}")
        active_timers[chat_id].cancel()
        del active_timers[chat_id]


def add_input_to_dm(input: InputLevel) -> Lead:
    print(input.type)
    dm_exists(input.chat_id)
    
    if input.type == Type.TEXT:
        lead = add_dm_text(input)
        dms = check_message_state_text(lead.chat_id)
        if dms != None:
            return dms
        return None
    elif input.type == Type.IMAGE:
        lead = add_dm_image(input)
        dms = check_message_state_image(lead.chat_id)
        if dms != None:
            return dms
        return None
    
    return None


def add_dm_text(input: InputLevel) -> Lead:
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

    message = f"{dm.dm1} {dm.dm2} {dm.dm3} {dm.dm4} {dm.dm5}"

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

    message = f"{dm.dm1} {dm.dm2} {dm.dm3} {dm.dm4} {dm.dm5}"

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


def check_message_state_text(chat_id: str) -> Lead:
    """Check message state and prepare data for bot trigger."""
    dm = DM_Level.get(chat_id)
    if not dm:
        print(f"No DM found for chat_id: {chat_id}")
        return None
    print(chat_id)
    print(dm)
    DM1 = dm.dm1
    DM2 = dm.dm2
    DM3 = dm.dm3
    DM4 = dm.dm4
    DM5 = dm.dm5
    
    is_first_message = (
        DM1
        and DM1 != ""
        and (not DM2 or DM2 == "")
    )
    
    # Check if 5 messages reached
    has_five_messages = (
        DM1 and DM1 != "" and
        DM2 and DM2 != "" and
        DM3 and DM3 != "" and
        DM4 and DM4 != "" and
        DM5 and DM5 != ""
    )
    
    print("Is first message?", is_first_message)
    print("Has 5 messages?", has_five_messages)

    if is_first_message:
        print("✅ First message - starting 30s timer")
        start_timer(chat_id)
        return None  # Don't process yet, wait for timer or 5 messages
    elif has_five_messages:
        print("✅ 5 messages reached - processing now!")
        cancel_timer(chat_id)
        return dm.Lead
    else:
        print("Message added to batch")
        return None


def check_message_state_image(chat_id: str) -> Lead:
    """Check message state and prepare data for bot trigger."""
    dm = DM_Level.get(chat_id)
    if not dm:
        print(f"No DM found for chat_id: {chat_id}")
        return None
    print(chat_id) 
    print(dm)
    DM1 = dm.dm1
    DM2 = dm.dm2
    DM3 = dm.dm3
    DM4 = dm.dm4
    DM5 = dm.dm5
    
    is_first_message = (
        DM1
        and DM1 != ""
        and (not DM2 or DM2 == "")
    )
    
    # Check if 5 messages reached
    has_five_messages = (
        DM1 and DM1 != "" and
        DM2 and DM2 != "" and
        DM3 and DM3 != "" and
        DM4 and DM4 != "" and
        DM5 and DM5 != ""
    )

    print("Is first message?", is_first_message)
    print("Has 5 messages?", has_five_messages)

    if is_first_message:
        print("✅ First message - starting 30s timer")
        start_timer(chat_id)
        return None  # Don't process yet, wait for timer or 5 messages
    elif has_five_messages:
        print("✅ 5 messages reached - processing now!")
        cancel_timer(chat_id)
        return dm.Lead
    else:
        print("Message added to batch")
        return None


def dm_exists(chat_id: str) -> None:
    if chat_id not in DM_Level:
        DM_Level[chat_id] = DM(
            Lead=None,
            dm1='',
            dm2='',
            dm3='',
            dm4='',
            dm5=''
        )