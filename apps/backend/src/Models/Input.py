from dataclasses import dataclass
from enum import Enum

# Use relative imports since this file is inside src/models/
from src.models.ImageInput import Image
from src.models.AudioInput import Audio
class Type(Enum):
    TEXT = 1
    IMAGE = 2
    AUDIO = 3

@dataclass
class InputLevel:
    chat_id: str
    user_id: str
    user: str
    type: Type
    message: str
    image: Image
    audio: Audio