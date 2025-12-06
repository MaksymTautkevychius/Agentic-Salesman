from dotenv import load_dotenv 
from src.agents.memory_manager.chat_memory_history import AIMemoryManager
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
import os

OpenAPI = os.environ["OPEN_API_KEY"]
openai_gpt5 = 'gpt-5'
openai_gpt4_1='gpt-4.1'
openai_gpt5mini='gpt-5-mini'
alibaba_qwen_3max='qwen3-max'



def main_agent_invoke(chatid:str, last_message: str):

    main_prompt_path = os.getenv("main_prompt")
    load_dotenv()
    with open(main_prompt_path, "r", encoding="utf-8") as f:
        main_prompt = f.read()

    memory = AIMemoryManager(chatid)
    history_list = memory.get_messages_for_langchain()  
    langchain_history = []
    for role, content in history_list:
        if role == "human":
            langchain_history.append(HumanMessage(content=content))
        else:
            langchain_history.append(AIMessage(content=content))

    system_prompt = SystemMessagePromptTemplate.from_template(
       main_prompt
    )
    user_prompt= HumanMessagePromptTemplate.from_template(
    """
    CONVERSATION CONTEXT
    **User's Last Message:** {last_message}

    EXTRACTED INFORMATION
    Watch Name/Details: {watch_name}
    Budget Mentioned: {budget}
    Message Type: {message_type}
    Purchase Timing: {purchase_time}


    RESPONSE REQUIREMENTS
    Respond as Adam using the System Prompt rules
    Follow the flow sequence (0→1→2→3→4) based on current state
    Use the extracted information above to determine next action
    If Watch Name is incomplete or unclear, start at step 0
    If Watch Name is complete, proceed to appropriate flow step
    Match message style to Type (text/image)
    Consider Purchase Timing for deposit logic

    CRITICAL REMINDERS
    Ask ONLY ONE question per response
    Keep it short and WhatsApp-casual
    Never mention tools, databases, or being AI
    Use exact template wording on first use
    Paraphrase on repeat questions
    No markdown, no formatting, no emojis
    Don't start with "Got it", "Sure", "Okay", etc.

    NEXT ACTION
    Based on the above information, determine:
    1. Which flow step applies?
    2. What information is missing?
    3. What's the single best question or response right now?


    """,
    input_variables=["last_message","watch_name", "budget", "message_type", "purchase_time"]
    )
    main_agent_prompt = ChatPromptTemplate.from_messages([
        ('system',system_prompt),
        ('human',user_prompt)
    ])
