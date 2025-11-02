import sys
from pathlib import Path


backend_path = Path(__file__).parent.parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from src.models.Lead import Lead


def process_message(lead: Lead):
    pass