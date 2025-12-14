from typing import TypedDict,List,Dict
class MainAgentState(TypedDict, total=False):
    name: str
    WatchName: str
    Budget: float
    Type: str
    message: str
    OCR_message: str
    sessionid: str
    response :str
    is_watch_inquiry: bool
    time : str
    has_name : bool
    is_already_given : bool
    ready_to_purchase : bool
    history: List[Dict[str, str]]
    