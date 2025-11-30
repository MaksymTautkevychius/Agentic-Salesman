from typing import TypedDict
from src.models.Lead import Lead
from src.models.audio_input import AudioInput
from src.models.image_input import ImageInput


class PreProcessingAgentState(TypedDict):
    message : str
    type: str
    username: str
    lead: Lead
    image: ImageInput
    audio: AudioInput
    OCR_message: str