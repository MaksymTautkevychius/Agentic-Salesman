import sys
from pathlib import Path

from dataclasses import dataclass
from typing import Optional
from src.models.ImageInput import Image
from src.models.AudioInput import Audio
from src.models.Input import Type

@dataclass
class Lead:
    chat_id: str
    user_id: str
    user: str
    type: Type
    message: str
    image: Optional[Image]
    audio: Optional[Audio]