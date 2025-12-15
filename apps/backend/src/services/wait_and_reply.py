from src.models.Lead import Lead
from src.models.Lead import Type
from src.models.DM.input import InputLevel
from src.pre_processing.input_processing import add_input_to_dm, set_timeout_callback, clear_dm
from src.graphs.pre_processing_graph import invoke_pre_processing
from src.graphs.main_flow_graph import invoke_main_bot


def process_message_and_generate_reply(lead: Lead) -> None:
    """
    Sends message or bunch of messages to the pre_processing and main graphs
    """
    if lead is None:
        print("Warning: Lead is None, skipping processing")
        return
    
    value,ocr_message = invoke_pre_processing(lead)
    response,url= invoke_main_bot(value,ocr_message,lead.chat_id)
    print(response,url)
    print(f"Result: {value} and {ocr_message}")
    print(f" Processing complete for chat_id: {lead.chat_id}")
    clear_dm(lead.chat_id)
    

def send_summarization_to_user(chatd_id: str, message: str) -> None:
    """
    After user reaching the desired point, all of the users data sends to the required user
    """
    pass


async def send_message_to_user(lead: Lead) -> None:
    """
    Sends message to the user via telegram bot
    """
    pass


def add_new_data_to_dm(input: InputLevel) -> None:
    """
    Adds the data from telegram bot to dm messages in a processed state
    """
    new_messages = add_input_to_dm(input)
    
    # Check if new_messages is None before processing
    if new_messages is None:
        print("No immediate processing (waiting for more messages or timeout)")
        return
    
    process_message_and_generate_reply(new_messages)


# Set the callback so timer can trigger processing
set_timeout_callback(process_message_and_generate_reply)