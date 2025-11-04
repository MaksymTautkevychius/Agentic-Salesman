import sys
from pathlib import Path
from typing import TypedDict
from langgraph.graph import START, END, StateGraph
from IPython.display import Image, display
from src.graphs.PreProcessingAgentState import PreProcessingAgentState
from src.models.Lead import Lead
