from src.models.lead import Lead
from src.models.DM.input import InputLevel
from src.pre_processing.input_processing import add_input_to_dm, check_message_state_text
from src.graphs.pre_processing_graph import fill_pre_processing_with_data,invoke_pre_processing

def process_message_and_generate_reply(lead: Lead, graph: object)-> object:
    """
    Sends bunch of messages to the pre_processing and main graphs
    """
    invoke_pre_processing(graph,fill_pre_processing_with_data(lead))
    pass

def send_summarization_to_user(chatd_id: str, message: str)->None:
    """
    After user reaching the desired point, all of the users data sends to the required user
    """
    pass

async def send_message_to_user(lead: Lead)->None:
    """
    Sends message to the user via telegram bot
    """
    pass

def add_new_data_to_dm(input: InputLevel) -> None:
    """
    Adds the data from telegram bot to dm messages in a processed state
    """
    add_input_to_dm(input)
    value = check_message_state_text(input.chat_id)
    if value!=None:
        process_message_and_generate_reply(value)
    