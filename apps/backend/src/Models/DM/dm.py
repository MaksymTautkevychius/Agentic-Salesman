from dataclasses import dataclass
from typing import Optional
from src.models.lead import Lead
@dataclass
class DM:
    Lead: Lead
    dm1: Optional[str] = None
    dm2: Optional[str] = None
    dm3: Optional[str] = None
    dm4: Optional[str] = None
    dm5: Optional[str] = None
