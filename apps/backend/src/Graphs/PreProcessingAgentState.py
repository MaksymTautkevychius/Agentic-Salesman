from typing import TypedDict
from src.models import Lead
class PreProcessingAgentState(TypedDict):
    message : str
    type: str
    username: str
    lead: Lead