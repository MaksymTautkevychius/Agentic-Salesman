import sys
import base64
from pathlib import Path
from langgraph.graph import START, END, StateGraph
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_community.chat_models.openai import ChatOpenAI
from langchain_classic.schema import HumanMessage
from src.graphs.pre_processing_agent_state import PreProcessingAgentState
from src.models.Lead import Lead
from src.models.DM.input import Type
from src.agents.Prompts.prompt import image_OCR_prompt

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# Define processing functions
def text_processing(state: PreProcessingAgentState) -> PreProcessingAgentState:
    """Text is already put in the needed state, this function created in case for needed changes in prompt"""
    return state


def photo_processing(state: PreProcessingAgentState) -> PreProcessingAgentState:
    """processes image from the user"""
    print('photo started to being processed')
    
    if state.get('image') is None:
        print("Warning: No image found in state")
        state["OCR_message"] = "No image provided"
        return state
    
    llm = ChatOpenAI(model="gpt-4o-mini")  # Changed model name
    
    # Use file_path directly - don't concatenate with file_name
    file_path = state['image'].file_path
    print(f"Processing image at: {file_path}")
    
    try:
        with open(file_path, "rb") as f:
            img_data = f.read()
            print(f"Image data read: {len(img_data)} bytes")
            img_base64 = base64.b64encode(img_data).decode("utf-8")
            print(f"Base64 encoded: {len(img_base64)} characters")
        
        message = HumanMessage(
            content=[
                {"type": "text", "text": f"{image_OCR_prompt}"},
                {
                    "type": "image_url", 
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_base64}"
                    }
                }
            ]
        )
        state["OCR_message"] = llm.invoke([message]).content
        print("Image processed successfully")
        print(f"OCR Result: {state['OCR_message']}")
    except FileNotFoundError as e:
        print(f"Error: Image file not found at {file_path}")
        state["OCR_message"] = f"Image file not found: {file_path}"
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        import traceback
        traceback.print_exc()
        state["OCR_message"] = f"Error processing image: {str(e)}"
    
    return state


def audio_processing(state: PreProcessingAgentState) -> PreProcessingAgentState:
    """Currently not finished"""
    return state


def pre_process_input_cond(state: PreProcessingAgentState) -> str:
    """Route to the appropriate processing node based on lead type"""
    lead_type = state.get("type")
    
    if lead_type == Type.TEXT:
        return "text_processing_operation"
    elif lead_type == Type.IMAGE:
        return "photo_processing_operation"
    elif lead_type == Type.AUDIO:
        return "audio_processing_operation"
    else:
        # Default fallback
        return "text_processing_operation"


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


# Create processor instance but DON'T compile yet
processor = PreProcessingPipeline()


# Export this function to be called from main
def generate_pre_processing_graph():
    """Initialize and compile the pre-processing graph"""
    processor.generate_pre_processing_graph()


def fill_pre_processing_with_data(Lead: Lead):
    state = PreProcessingAgentState(
        message=Lead.message,
        type=Lead.type,
        username=Lead.user,
        image=Lead.image,
        audio=Lead.audio
    )
    return state


def invoke_pre_processing(lead: Lead) -> object:
    """Invoke the pre-processing graph and return the final state"""
    state = PreProcessingAgentState(
        message=lead.message or 'none',
        type=lead.type,
        username=lead.user,
        lead=lead,
        image=lead.image,
        audio=lead.audio,
        OCR_message=""
    )
    if processor.pre_processing_graph_compiled is None:
        raise ValueError("Graph is not compiled. Call generate_pre_processing_graph() first")    
    processor.pre_processing_graph_compiled.invoke(state)
    return  state.get('message', 'none'), state.get('OCR_message', '')