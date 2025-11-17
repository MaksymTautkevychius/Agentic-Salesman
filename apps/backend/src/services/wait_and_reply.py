from src.models.lead import Lead
from src.models.lead import Type
from src.models.DM.input import InputLevel
from src.pre_processing.input_processing import add_input_to_dm, check_message_state_text
from apps.backend.src.graphs.pre_processing_graph import fill_pre_processing_with_data,invoke_pre_processing
from apps.backend.src.graphs.pre_processing_agent_state import pr


def process_message_and_generate_reply(lead: Lead)-> None:
    """
    Sends message or  bunch of messages to the pre_processing and main graphs
    
    """
    invoke_pre_processing(lead)
    

def send_summarization_to_user(chatd_id: str, message: str)->None:
    """
    After user reaching the desired point, all of the users data sends to the required user
    
    """
    pass

async def send_message_to_user(lead: Lead)->None:
    """
    Sends message tob the user via telegram bot
    
    """
    pass

def add_new_data_to_dm(input: InputLevel) -> None:
    """
    Adds the data from telegram bot to dm messages in a processed state
    
    """
    new_messages = add_input_to_dm(input)
    process_message_and_generate_reply(new_messages)
    
    
        
   #if value!=None:
   #    process_message_and_generate_reply(value)
    