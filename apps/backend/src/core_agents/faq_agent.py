from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from src.agents.memory_manager.chat_memory_history import AIMemoryManager
from dotenv import load_dotenv
import os
load_dotenv()

OpenAPI = os.environ["OPENAI_API_KEY"]
llm = ChatOpenAI(temperature=0.2, model='gpt-4.1')

prompt_path = os.getenv("faq_prompt")

if not prompt_path:
    raise ValueError("faq_prompt path not found ")

with open(prompt_path, "r", encoding="utf-8") as f:
    prompt_text = f.read()

print(prompt_text)


def faq_agent_invoke(sessionid: str, message: str, OCR_message: str) -> str:

    memory = AIMemoryManager(sessionid)
    history_list = memory.get_conversation_buffer_memory()

    langchain_history = []
    for role, content in history_list:
        if role == "human":
            langchain_history.append(HumanMessage(content=content))
        else:  
            langchain_history.append(AIMessage(content=content))

    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_text),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "User Message: {input}\n\nOCR Extracted Text: {ocr_text}"),
    ])

    memory= AIMemoryManager('123456789')
    memory.get_conversation_buffer_memory()

    agent= create_agent(
        llm=llm,
        prompt=prompt,
        memory= memory
    )
    
    response = agent.invoke({
        "input": message,
        "ocr_text": OCR_message
    })

    ai_output = response.content if hasattr(response, "content") else str(response)

    memory.add_message("human", message)
    memory.add_message("ai", ai_output)
    
    return ai_output
