from src.telegram_handler.telegram_input_handler import start_telegram_bot
from src.graphs.pre_processing_graph import generate_pre_processing_graph
from src.agents.memory_manager.chat_memory_history import example_usage
from src.core_agents.faq_agent import faq_agent_invoke
from src.core_agents.name_agent import name_agent_invoke

if __name__ == "__main__":
     generate_pre_processing_graph()
     #example_usage()
     #faq_agent_invoke('123456789',"I want newest Golden rolex","Rolex")
     name_agent_invoke('123456789',"I want newest Golden rolex")
     start_telegram_bot()
     