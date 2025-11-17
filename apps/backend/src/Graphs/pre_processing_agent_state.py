from typing import TypedDict
from src.models.lead import Lead
from src.models.audio_input import AudioInput
from src.models.image_input import Image


class PreProcessingAgentState(TypedDict):
    message : str
    type: str
    username: str
    lead: Lead
    image: Image
    audio: AudioInput