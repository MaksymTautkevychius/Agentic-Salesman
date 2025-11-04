from dataclasses import dataclass
from typing import Optional
from src.models.image_input import Image
from src.models.audio_input import AudioInput
from src.models.DM.input import Type

@dataclass
class Lead:
    chat_id: str
    user_id: str
    user: str
    type: Type
    message: str
    image: Optional[Image]
    audio: Optional[AudioInput]