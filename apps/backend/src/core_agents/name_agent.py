from dotenv import load_dotenv
import os

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from src.agents.memory_manager.chat_memory_history import AIMemoryManager



load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.2
)

prompt_path = os.getenv("name_prompt")
with open(prompt_path, "r", encoding="utf-8") as f:
    system_prompt_text = f.read()


def name_agent_invoke(sessionid: str, message: str):

    memory = AIMemoryManager(sessionid)
    history_list = memory.get_messages_for_langchain()

    chat_history = []
    for role, content in history_list:
        if role == "human":
            chat_history.append(HumanMessage(content=content))
        else:
            chat_history.append(AIMessage(content=content))

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_text),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])

    agent = prompt | llm
    response = agent.invoke({
        "chat_history": chat_history,
        "input": message
    })

    ai_output = response.content

    memory.add_message("human", message)
    memory.add_message("ai", ai_output)

    return ai_output
