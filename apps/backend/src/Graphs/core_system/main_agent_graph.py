from langgraph.graph import START, END, StateGraph
from IPython.display import Image, display
from src.graphs.pre_processing_agent_state import PreProcessingAgentState
from src.graphs.core_system.main_agent_state import AgentState

def extractor(state: AgentState):
    state["message"] = "Extracted user info: name, WatchName, Budget..."
    return state


def name_faq_agent(state: AgentState):
    state["message"] = "Handled FAQ and name-related queries."
    return state


def helper_agent(state: AgentState):
    state["message"] = "Aggregated supporting information."
    return state


def salesman_agent(state: AgentState):
    state["message"] = "Prepared sales communication."
    return state


def main_agent(state: AgentState):
    state["message"] = "Main Agent coordinating between agents."
    return state


def output_node(state: AgentState):
    state["message"] = f"Output ready: {state.get('message', '')}"
    return state

def memory_manager(state: AgentState):
    state["message"] = f"Output ready: {state.get('message', '')}"
    return state


def main_router(state: AgentState) -> str:
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



graph = StateGraph(AgentState)


def generate_main_system()-> None:
    # Define nodes
    graph.add_node("Extractor", extractor)
    graph.add_node("Main Agent", main_agent)
    graph.add_node("Router", lambda state: state) 
    graph.add_node("Name+FAQ Agent", name_faq_agent)
    graph.add_node("Helper Agent", helper_agent)
    graph.add_node("Salesman Agent", salesman_agent)
    graph.add_node("Output", output_node)
    graph.add_node("Memory Manager", memory_manager)
    graph.add_edge(START, "Memory Manager")
    graph.add_edge( "Memory Manager", "Extractor")
    graph.add_edge("Extractor", "Router")

    graph.add_conditional_edges(
        "Router",
        main_router,
        {
            "faq_route": "Name+FAQ Agent",
            "helper_route": "Helper Agent",
            "sales_route": "Main Agent",
        },
    )

    graph.add_edge("Extractor", "Salesman Agent")
    graph.add_edge("Name+FAQ Agent", "Output")
    graph.add_edge("Helper Agent", "Output")
    graph.add_edge("Main Agent", "Output")
    # Define end of flow
    graph.add_edge("Output", END)
    graph
