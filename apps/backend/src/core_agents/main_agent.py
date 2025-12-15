from dotenv import load_dotenv
import os
from typing import Optional
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate
)

from src.agents.memory_manager.chat_memory_history import AIMemoryManager
from src.tools.watch_tool import find_and_download_watch



load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1",
    temperature=0.2
)


class StructuredMainOutput(BaseModel):
    response: str = Field(description="Response for the user")
    image_url: Optional[str] = Field(
        description="Image URL if watch found",
        default=None
    )
    needs_tool: bool = Field(
        description="Whether tool call is needed",
        default=False
    )



def main_agent_invoke(sessionid: str, message: str, OCR_message: str):

    # Load system prompt
    main_prompt_path = os.getenv("main_prompt")
    with open(main_prompt_path, "r", encoding="utf-8") as f:
        system_prompt_text = f.read()

    memory = AIMemoryManager(sessionid)
    chat_history = memory.get_conversation_buffer_memory()

    # Prompts
    system_prompt = SystemMessagePromptTemplate.from_template(
        system_prompt_text
    )

    human_prompt = HumanMessagePromptTemplate.from_template(
        """
        CONVERSATION HISTORY
        {chat_history}

        USER MESSAGE
        {last_message}

        OCR TEXT
        {ocr_text}

        EXTRACTED INFORMATION
        Watch Name/Details: {watch_name}
        Budget Mentioned: {budget}
        Message Type: {message_type}
        Purchase Timing: {purchase_time}

        RESPONSE REQUIREMENTS
        Respond as Adam using the System Prompt rules
        Follow the flow sequence (0→1→2→3→4)
        Ask ONLY ONE question
        Keep it short and WhatsApp-casual
        Never mention tools, databases, or being AI
        No markdown, no emojis
        """
    )

    prompt = ChatPromptTemplate.from_messages([
        system_prompt,
        human_prompt
    ])

    # Bind tools + structured output
    agent = (
        prompt
        | llm.bind_tools([find_and_download_watch])
             .with_structured_output(StructuredMainOutput)
    )

    # Invoke (ALL variables must be present)
    result: StructuredMainOutput = agent.invoke({
        "chat_history": chat_history,
        "last_message": message,
        "ocr_text": OCR_message,
        "watch_name": "",
        "budget": "",
        "message_type": "text",
        "purchase_time": ""
    })

    memory.add_message("human",message)
    memory.add_message("ai",result.response)
    print(result.response)
    print(result.image_url)
    return result.response, result.image_url
