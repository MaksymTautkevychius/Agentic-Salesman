from src.telegram_handler.telegram_input_handler import start_telegram_bot,start_telegram_bot_background
from src.graphs.pre_processing_graph import generate_pre_processing_graph
from src.graphs.main_flow_graph import generate_main_bot_graph
from src.telegram_handler.telegram_input_handler import start_telegram_bot_background, send_message_sync
from src.graphs.pre_processing_graph import generate_pre_processing_graph
from src.graphs.main_flow_graph import generate_main_bot_graph
import time
#from src.agents.extractor.core_extractor import test_extract_data 
from src.agents.memory_manager.chat_memory_history import AIMemoryManager
from src.core_agents.faq_agent import faq_agent_invoke
from src.core_agents.main_agent import main_agent_invoke
from src.core_agents.name_agent import name_agent_invoke

if __name__ == "__main__":
     #test_extract_data()
     #example_usage()
     #print(faq_agent_invoke('123456789',"I want newest Golden rolex","Rolex"))
     #print(name_agent_invoke('123456789',"I want newest Golden rolex"))
     #memory= AIMemoryManager('123456789')
     #memory.get_conversation_buffer_memory()
     start_telegram_bot_background()
     generate_pre_processing_graph()
     generate_main_bot_graph()
     #main_agent_invoke('1234','1234')

     #do. not. touch.
     
     try:
         while True:
             time.sleep(1)
     except KeyboardInterrupt:
         print("stopped")