from dataclasses import dataclass
from typing import Optional
from enum import Enum

class Type(Enum):
    TEXT = 1,
    IMAGE = 2,
    AUDIO = 3

@dataclass
class InputLevel:
    chat_id: str
    user_id: str
    user: str
    type: Type
    message: str
    file_path: str
