from typing import TypedDict
class MainAgentState(TypedDict, total=False):
    name: str
    WatchName: str
    Budget: float
    Type: str
    message: str