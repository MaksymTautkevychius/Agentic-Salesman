from typing import TypedDict
from  src.models.Lead import Lead
class AgentState(TypedDict, total=False):
    lead: Lead
    name: str
    WatchName: str
    Budget: float
    Type: str
    message: str