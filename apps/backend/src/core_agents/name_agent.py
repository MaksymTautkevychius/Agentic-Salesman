from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from src.agents.memory_manager.chat_memory_history import AIMemoryManager
from dotenv import load_dotenv
from langchain.agents import create_agent
import os

load_dotenv()


OpenAPI = os.environ["OPENAI_API_KEY"]
llm = ChatOpenAI(temperature=0.2, model='gpt-4.1')

prompt_path = os.getenv("name_prompt")

with open(prompt_path, "r", encoding="utf-8") as f:
    prompt_text = f.read()

print(prompt_text)


def name_agent_invoke(sessionid: str, message: str):
    memory = AIMemoryManager(sessionid)
    history_list = memory.get_messages_for_langchain()


    langchain_history = []
    for role, content in history_list:
        if role == "human":
            langchain_history.append(HumanMessage(content=content))
        else: 
            langchain_history.append(AIMessage(content=content))

    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_text),
        MessagesPlaceholder(variable_name="chat_history"),  
        ("human", "{input}"),
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
        "chat_history": langchain_history, 
    })

    ai_output = response.content if hasattr(response, "content") else str(response)

    memory.add_message("human", message)
    memory.add_message("ai", ai_output)
    
    return ai_output