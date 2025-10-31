from Models.DM import DM 
from Models import InputLevel

DM_Level: dict[str, DM] = {}

def add_input_to_dm(input: InputLevel )-> None:

    if input.Type.TEXT:
        dm_exists(input)
    if input.Type.IMAGE:
        return
    if input.Type.AUDIO:
        return

def dm_exists(chat_id: str, input: InputLevel)-> None:
    if chat_id in DM_Level:
        return True
    else: 
        DM_Level.update(chat_id,input)
        return False