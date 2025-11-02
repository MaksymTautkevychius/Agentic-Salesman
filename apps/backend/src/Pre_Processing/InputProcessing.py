import sys
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).parent.parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from src.models.Lead import Lead
from src.models.DM import DM
from src.models.Input import InputLevel, Type

# Fix the import - use src. prefix
from src.services.WaitAndReply import process_message

DM_Level: dict[str, DM] = {}


def add_input_to_dm(input: InputLevel) -> None:
    dm_exists(input.chat_id)
    # Fix: Compare with Type enum correctly
    if input.type == Type.TEXT:
        add_dm_text(input)
    elif input.type == Type.IMAGE:
        return
    elif input.type == Type.AUDIO:
        return


def add_dm_text(input: InputLevel) -> None:
    dm = DM_Level.get(input.chat_id)
    
    if dm.dm1 == '':
        dm.dm1 = input.message
    elif dm.dm2 == '':
        dm.dm2 = input.message
    elif dm.dm3 == '':
        dm.dm3 = input.message
    elif dm.dm4 == '':
        dm.dm4 = input.message
    elif dm.dm5 == '':
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


def send_to_bot(chat_id: str) -> None:
    """Check message state and prepare data for bot trigger."""
    dm = DM_Level.get(chat_id)
    if not dm:
        print(f"No DM found for chat_id: {chat_id}")
        return

    DM1 = dm.dm1
    DM2 = dm.dm2
    is_first_message = (
        DM1
        and DM1 != ""
        and (not DM2 or DM2 == "")
    )

    print("Is first message?", is_first_message)

    if is_first_message:
        process_message(dm.Lead)
    else:
        print("Message skipped")


def dm_exists(chat_id: str) -> None:
    if chat_id not in DM_Level:
        # Fix: Create proper DM instance
        DM_Level[chat_id] = DM(
            Lead=None,
            dm1='',
            dm2='',
            dm3='',
            dm4='',
            dm5=''
        )


def add_new_data(input: InputLevel) -> None:
    add_input_to_dm(input)
    send_to_bot(input.chat_id)