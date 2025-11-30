import sys
from src.models.DM.dm import DM
from src.models.DM.input import InputLevel, Type
from pathlib import Path
from src.models.Lead import Lead

backend_path = Path(__file__).parent.parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))


"""DMs buffer Of all users writing now"""
DM_Level: dict[str, DM] = {}


def add_input_to_dm(input: InputLevel) -> Lead:
    print(input.type)
    dm_exists(input.chat_id)
    if input.type == Type.TEXT:
        lead = add_dm_text(input)
        dms = check_message_state_text(lead.chat_id)
        if dms != None:
            return dms
        return None  # ← Add this
    elif input.type == Type.IMAGE:
        lead = add_dm_image(input)
        dms = check_message_state_image(lead.chat_id)
        if dms != None:
            return dms
        return None  # ← Add this
    
    return None  # ← Add this as fallback


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
        return None  # ← Add explicit return
    print(chat_id)
    print(dm)
    DM1 = dm.dm1
    DM2 = dm.dm2
    is_first_message = (
        DM1
        and DM1 != ""
        and (not DM2 or DM2 == "")
    )
    print("Is first message?", is_first_message)

    if is_first_message:
        print("added new lead")
        return dm.Lead
    else:
        print("Message skipped")
        return None  # ← Add explicit return


def check_message_state_image(chat_id: str) -> Lead:
    """Check message state and prepare data for bot trigger."""
    dm = DM_Level.get(chat_id)
    if not dm:
        print(f"No DM found for chat_id: {chat_id}")
        return None  # ← Add explicit return
    print(chat_id) 
    print(dm)
    DM1 = dm.dm1
    DM2 = dm.dm2
    is_first_message = (
        DM1
        and DM1 != ""
        and (not DM2 or DM2 == "")
    )

    print("Is first message?", is_first_message)

    if is_first_message:
        print("added new lead")
        return dm.Lead
    else:
        print("Message skipped")
        return None  # ← Add explicit return


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