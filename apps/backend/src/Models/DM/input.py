from enum import Enum
from dataclasses import dataclass
from src.models.image_input import Image
from src.models.audio_input import AudioInput
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
    audio: AudioInput