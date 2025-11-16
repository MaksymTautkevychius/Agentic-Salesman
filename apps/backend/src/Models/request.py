from dataclasses import dataclass
from src.models.lead import Type
@dataclass
class PromptData():
    message : str
    purchase_info: str
    name: str
    message_type: Type