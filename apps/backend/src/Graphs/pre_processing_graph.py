import sys,base64
from pathlib import Path
from langgraph.graph import START, END, StateGraph
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_community.chat_models.openai import ChatOpenAI
from langchain_classic.schema import HumanMessage
from src.graphs.pre_processing_agent_state import PreProcessingAgentState
from src.models.lead import Lead
from src.agents.Prompts.prompt import image_OCR_prompt

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class PreProcessingPipeline:
    def __init__(self):
        self._pre_processing_graph = StateGraph(PreProcessingAgentState)
        self._pre_processing_graph_compiled = None

    @property
    def pre_processing_graph_compiled(self):
        return self._pre_processing_graph_compiled

    @pre_processing_graph_compiled.setter
    def pre_processing_graph_compiled(self, value):
        self._pre_processing_graph_compiled = value

    def generate_pre_processing_graph(self):

        
        self._pre_processing_graph.add_node("text_processing_node", text_processing)
        self._pre_processing_graph.add_node("photo_processing_node", photo_processing)
        self._pre_processing_graph.add_node("audio_processing_node", audio_processing)
        self._pre_processing_graph.add_node("router", lambda state: state)

        
        self._pre_processing_graph.add_edge(START, "router")

        self._pre_processing_graph.add_conditional_edges(
            "router",
            pre_process_input_cond,
            {
                "text_processing_operation": "text_processing_node",
                "photo_processing_operation": "photo_processing_node",
                "audio_processing_operation": "audio_processing_node"
            }
        )

        self._pre_processing_graph.add_edge("text_processing_node", END)
        self._pre_processing_graph.add_edge("photo_processing_node", END)
        self._pre_processing_graph.add_edge("audio_processing_node", END)

        self.pre_processing_graph_compiled = self._pre_processing_graph.compile()





pre_processing_graph = StateGraph(PreProcessingAgentState)
processor = PreProcessingPipeline()
processor.generate_pre_processing_graph()
def text_processing(state:PreProcessingAgentState) -> PreProcessingAgentState:
    """Text is already put in the needed state, this function created in case for needed changes in prompt"""
    return state

def photo_processing(state:PreProcessingAgentState) -> PreProcessingAgentState:
    """
    processes image from the user 
    """
    llm = ChatOpenAI(model="gpt-4.1-mini") 
    with open(f"{state['image'].file_path}{state['image'].file_name}.jpg", "rb") as f:
        img_data = f.read()
        img_base64 = base64.b64encode(img_data).decode("utf-8")
    message = HumanMessage(
        content=[
            {"type": "text", "text": f"{image_OCR_prompt}"},
            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{img_base64}"}
        ]
    )
    state["OCR_message"] = llm.invoke([message]).content
    return state

def audio_processing(state:PreProcessingAgentState) -> PreProcessingAgentState:
    """Currently not finished """
    return state

def pre_process_input_cond(state:PreProcessingAgentState, )-> PreProcessingAgentState:
    return state


def fill_pre_processing_with_data(Lead: Lead):
    state:PreProcessingAgentState = PreProcessingAgentState(
        message=Lead.message,
        type=Lead.type,
        username = Lead.user,
        image= Lead.image,
        audio=Lead.audio
    )
    return state

def invoke_pre_processing(lead: Lead) -> PreProcessingAgentState:
    """Invoke the pre-processing graph and return the final state"""

    state = PreProcessingAgentState(
        message=lead.message,
        type=lead.type,
        username=lead.user,
        lead=lead,
        image = lead.image,
        audio=lead.audio
    )
    if processor.pre_processing_graph_compiled is None:
        raise ValueError("Graph is not compiled. Pass a compiled graph instance")

    return processor.pre_processing_graph_compiled.invoke(state)