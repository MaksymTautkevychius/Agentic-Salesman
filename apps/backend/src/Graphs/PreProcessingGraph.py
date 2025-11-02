import sys
from pathlib import Path
from typing import TypedDict
from langgraph.graph import START, END, StateGraph
from IPython.display import Image, display
from src.graphs.PreProcessingAgentState import PreProcessingAgentState
from src.models.Lead import Lead




project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


pre_processing_graph = StateGraph(PreProcessingAgentState)

def text_processing(state:PreProcessingAgentState) -> PreProcessingAgentState:
    """This node is processing the text given from the user to create Output using Multi-Agent system """
    
    return state

def photo_processing(state:PreProcessingAgentState) -> PreProcessingAgentState:
    """Currently not finished """
    return state


    return state
def audio_processing(state:PreProcessingAgentState) -> PreProcessingAgentState:
    """Currently not finished """
    return state

def pre_process_input_cond(state:PreProcessingAgentState, )-> PreProcessingAgentState:
    return state





def generate_pre_processing_graph() -> object:
    pre_processing_graph.add_node("text_processing_node",text_processing)
    pre_processing_graph.add_node("photo_processing_node",photo_processing)
    pre_processing_graph.add_node("audio_processing_node",audio_processing)
    pre_processing_graph.add_node("router",lambda state: state)
    pre_processing_graph.add_edge(START,"router")
    pre_processing_graph.add_conditional_edges(
        "router",
        pre_process_input_cond,
        {
         "text_processing_operation":"text_processing_node",
         "photo_processing_operation":"photo_processing_node",
         "audio_processing_operation":"audio_processing_node"
        }
    )
    pre_processing_graph.add_edge("text_processing_node",END)
    pre_processing_graph.add_edge("photo_processing_node",END)
    pre_processing_graph.add_edge("audio_processing_node",END)
    pre_processing_graph_app = pre_processing_graph.compile()
    from IPython.display import Image, display
    display(Image(pre_processing_graph_app.get_graph().draw_mermaid_png()))
    return pre_processing_graph_app

