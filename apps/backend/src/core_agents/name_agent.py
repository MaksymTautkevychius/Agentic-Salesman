from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder,HumanMessagePromptTemplate
from langchain_core.chat_history import BaseChatMessageHistory
from src.agents.memory_manager.chat_memory_history import AIMemoryManager
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
llm=ChatOpenAI(temperature=0.2,model='gpt-4.1')


load_dotenv()


prompt_path = os.getenv("name_prompt")

with open(prompt_path, "r", encoding="utf-8") as f:
    prompt_text = f.read()
print(prompt_text)

def name_agent_invoke(chatid: str, message : str):

    memory = AIMemoryManager(chatid)
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
        ("placeholder", "{agent_scratchpad}"),
    ])

    chain = prompt | llm
    response = chain.invoke({
        "input": message,
        "chat_history": langchain_history,
        "agent_scratchpad": []
    })

    ai_output = response.content if hasattr(response, "content") else response
    print(ai_output)

    memory.add_message("human", message)
    memory.add_message("ai", ai_output)


