from langgraph.graph import START, END, StateGraph
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_community.chat_models.openai import ChatOpenAI
from langchain_classic.schema import HumanMessage
from src.graphs.main_agent_state import MainAgentState

from src.agents.extractor import core_extractor




def extractor(state: MainAgentState):
    state["message"] = "Extracted user info: name, WatchName, Budget..."
    return state


def name_faq_agent(state: MainAgentState):
    state["message"] = "Handled FAQ and name-related queries."
    return state



from langgraph.graph import StateGraph, START, END
from IPython.display import display, Image
from typing import TypedDict


def helper_agent(state: MainAgentState):
    state["message"] = "Aggregated supporting information."
    return state


def salesman_agent(state: MainAgentState):
    state["message"] = "Prepared sales communication."
    return state


def main_agent(state: MainAgentState):
    state["message"] = "Main Agent coordinating between agents."
    return state


def output_node(state: MainAgentState):
    state["message"] = f"Output ready: {state.get('message', '')}"
    return state

def memory_manager(state: MainAgentState):
    state["message"] = f"Output ready: {state.get('message', '')}"
    return state


def main_router(state: MainAgentState) -> str:
    """
    Route logic after Extractor:
    Choose which agent to activate next based on the Type.
    """
    user_type = state.get("Type", "").lower()
    if "faq" in user_type:
        return "faq_route"
    elif "help" in user_type:
        return "helper_route"
    else:
        return "sales_route"

class MainBotPipeline:
    def __init__(self):
        self.main_graph = StateGraph(MainAgentState)
        self.main_graph_compiled= None
    @property
    def main_graph_compiled(self):
        return self._main_graph_compiled

    @main_graph_compiled.setter
    def main_graph_compiled(self, value):
        self._main_graph_compiled = value
    
    def generate_main_bot(self):
        _main_graph_compiled = StateGraph(MainAgentState)


        self._main_graph_compiled.add_node("Extractor", extractor)
        self._main_graph_compiled.add_node("Main Agent", main_agent)
        self._main_graph_compiled.add_node("Router", lambda state: state) 
        self._main_graph_compiled.add_node("Name+FAQ Agent", name_faq_agent)
        self._main_graph_compiled.add_node("Helper Agent", helper_agent)
        self._main_graph_compiled.add_node("Salesman Agent", salesman_agent)
        self._main_graph_compiled.add_node("Output", output_node)
        self._main_graph_compiled.add_node("Memory Manager", memory_manager)

       
        self._main_graph_compiled.add_edge(START, "Memory Manager")
        self._main_graph_compiled.add_edge( "Memory Manager", "Extractor")

 
        self._main_graph_compiled.add_edge("Extractor", "Router")
        self._main_graph_compiled.add_conditional_edges(
            "Router",
            main_router,
            {
                "faq_route": "Name+FAQ Agent",
                "helper_route": "Helper Agent",
                "sales_route": "Main Agent",
            },
        )


        self._main_graph_compiled.add_edge("Extractor", "Salesman Agent")
        self._main_graph_compiled.add_edge("Name+FAQ Agent", "Output")
        self._main_graph_compiled.add_edge("Helper Agent", "Output")
        self._main_graph_compiled.add_edge("Main Agent", "Output")


        self._main_graph_compiled.add_edge("Output", END)


        self.main_graph_compiled = self._main_graph_compiled.compile()

processor = MainBotPipeline()



def generate_main_bot_graph():
    processor.generate_main_bot()

def fill_pre_processing_with_data(last_message:str, OCR_Message:str):
    state = MainAgentState(
        
    )
    return state


def invoke_pre_processing() -> object:
    """Invoke the pre-processing graph and return the final state"""
    state = MainAgentState(
        
    )
    if processor.main_graph_compiled is None:
        raise ValueError("Graph is not compiled. Call generate_main_bot() first")    
    processor.main_graph_compiled.invoke(state)
    return  state.get('message', 'none'), state.get('OCR_message', '')