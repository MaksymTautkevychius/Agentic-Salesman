from dataclasses import dataclass
from src.models.Lead import Type
@dataclass
class PromptData():
    message : str
    purchase_info: str
    name: str
    message_type: Type