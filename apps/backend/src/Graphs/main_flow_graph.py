from langgraph.graph import START, END, StateGraph
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_community.chat_models.openai import ChatOpenAI
from langchain_classic.schema import HumanMessage
from src.graphs.main_agent_state import MainAgentState
from src.agents.memory_manager.chat_memory_history import AIMemoryManager 
from src.agents.extractor import core_extractor
from src.core_agents.faq_agent import faq_agent_invoke
from src.core_agents.name_agent import name_agent_invoke
from src.core_agents.main_agent import main_agent_invoke
from src.telegram_handler.telegram_input_handler import send_message_sync,send_image_sync


def extractor(state: MainAgentState):
    data = core_extractor.extract_data(state["message"],state["OCR_message"],state['history'])
    return  {
        **state,
        "name": data.get("name"),
        "Budget": data.get("budget_amount"),
        "is_watch_inquiry": data.get("is_watch_inquiry"),
        "has_name" : data.get("has_name"),
        "time": data.get("time"),
        "is_already_given": data.get("is_already_given: "),
        "ready_to_purchase" :  data.get("ready_to_purchase")
    }


def name_faq_agent(state: MainAgentState):
    state["response"] = name_agent_invoke(state["sessionid"],state["message"],state['history'])
    send_message_sync(state['sessionid'],state["response"])
    return state

def helper_agent(state: MainAgentState):
    state["response"] = faq_agent_invoke(state["sessionid"],state["message"],state['history'])
    send_message_sync(state['sessionid'],state["response"])
    return state 


def salesman_agent(state: MainAgentState):
    return state


def main_agent_graph_invoke(state: MainAgentState):
    state["response"],state["image_url"] = main_agent_invoke(state["sessionid"],state["message"],state["OCR_message"])
    if state["image_url"]!=None:
        send_image_sync(state['sessionid'],state["image_url"])
    send_message_sync(state['sessionid'],state["response"])
    return state


def output_node(state: MainAgentState):
    state["message"] = f"Output ready: {state.get('message', '')}"
    return state

def memory_manager(state: MainAgentState):
    manager = AIMemoryManager(state['sessionid'])
    state['history'] = manager.retrieve_messages()
    manager.add_message('human',f"{state['message']}, ocr from image: {state['OCR_message']}")
    return state


def main_router(state: MainAgentState) -> str:
    """
    Route logic after Extractor:
    Choose which agent to activate next based on the stage
    """
    if state["has_name"]!=False:
        return "faq_route"
    elif state["is_watch_inquiry"]==True:
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


        self.main_graph.add_node("Extractor", extractor)
        self.main_graph.add_node("Main Agent", main_agent_graph_invoke)
        self.main_graph.add_node("Router", lambda state: state) 
        self.main_graph.add_node("Name+FAQ Agent", name_faq_agent)
        self.main_graph.add_node("Helper Agent", helper_agent)
        self.main_graph.add_node("Salesman Agent", salesman_agent)
        self.main_graph.add_node("Output", output_node)
        self.main_graph.add_node("Memory Manager", memory_manager)

       
        self.main_graph.add_edge(START, "Memory Manager")
        self.main_graph.add_edge( "Memory Manager", "Extractor")

 
        self.main_graph.add_edge("Extractor", "Router")
        self.main_graph.add_conditional_edges(
            "Router",
            main_router,
            {
                "faq_route": "Name+FAQ Agent",
                "helper_route": "Helper Agent",
                "sales_route": "Main Agent",
            },
        )


        self.main_graph.add_edge("Main Agent", "Salesman Agent")
        self.main_graph.add_edge("Name+FAQ Agent", "Output")
        self.main_graph.add_edge("Helper Agent", "Output")
        self.main_graph.add_edge("Main Agent", "Output")


        self.main_graph.add_edge("Output", END)


        self.main_graph_compiled = self.main_graph.compile()

processor = MainBotPipeline()



def generate_main_bot_graph():
    processor.generate_main_bot()


def invoke_main_bot(_message : str, OCR_message : str, sessionid : str) -> object:
    """Invoke the pre-processing graph and return the final state"""
    state = MainAgentState(
        name='',
        WatchName='',
        Budget='',
        Type='',
        message=_message,
        sessionid=sessionid,
        OCR_message=OCR_message
    )
    if processor.main_graph_compiled is None:
        raise ValueError("Graph is not compiled. Call generate_main_bot() first")    
    processor.main_graph_compiled.invoke(state)
    return  state.get('response', 'none'), state.get('OCR_message', '')