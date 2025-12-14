from dotenv import load_dotenv 
from src.agents.memory_manager.chat_memory_history import AIMemoryManager
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from src.tools.watch_tool import find_and_download_watch
import os

from dotenv import load_dotenv

load_dotenv()

OpenAPI = os.environ["OPENAI_API_KEY"]

OpenAPI = os.environ["OPENAI_API_KEY"]
llm = ChatOpenAI(temperature=0.2, model='gpt-4.1')



def main_agent_invoke(chatid: str, message : str, OCR_message :str):

    main_prompt_path = os.getenv("main_prompt")
    load_dotenv()
    with open(main_prompt_path, "r", encoding="utf-8") as f:
        main_prompt = f.read()

    memory= AIMemoryManager('123456789')
    memory.get_conversation_buffer_memory()

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
    prompt = ChatPromptTemplate.from_messages([
        ('system',system_prompt),
        ('human',user_prompt)
    ])
    agent= create_agent(
        memory=memory,
        llm=llm,
        prompt=prompt,
        tools=find_and_download_watch
    )
    response = agent.invoke({
        "input": message,
        "ocr_text": OCR_message
    })
    ai_output,image = response.content if hasattr(response, "content") else str(response)
    return ai_output,image
