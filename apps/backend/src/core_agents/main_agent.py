from dotenv import load_dotenv
import os
import getpass

from langchain_qwq import ChatQwen
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_classic.memory import ConversationBufferMemory

from src.tools.watch_tool import WatchTool

load_dotenv()

if not os.getenv("DASHSCOPE_API_KEY"):
    os.environ["DASHSCOPE_API_KEY"] = getpass.getpass("Enter your Dashscope API key: ")

llm = ChatQwen(
    model="qwen3-max",
    temperature=0.2,
    reasoning_effort="high"
)

class SessionMemoryManager:
    def __init__(self):
        self._memories = {}

    def get_memory(self, sessionid: str):
        if sessionid not in self._memories:
            self._memories[sessionid] = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                input_key="input",
                output_key="output"
            )
        return self._memories[sessionid]

memory_manager = SessionMemoryManager()

def main_agent_invoke(sessionid: str, message: str, OCR_message: str = ""):
    print(f"Starting agent for session: {sessionid}")

    main_prompt_path = os.getenv("main_prompt")
    with open(main_prompt_path, "r", encoding="utf-8") as f:
        system_prompt_text = f.read()

    memory = memory_manager.get_memory(sessionid)

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_text + """

IMPORTANT TOOL USAGE RULES
- If you know the specific watch model or reference, CALL WatchTool
- When calling WatchTool, ALWAYS pass:
  watch_name = concise watch reference string
- Never explain the tool call
- Never mention databases or AI
"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    tools = [WatchTool]

    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3,
        return_intermediate_steps=True
    )

    full_message = message
    if OCR_message:
        full_message += f"\n\nOCR TEXT:\n{OCR_message}"

    result = agent_executor.invoke({
        "input": full_message
    })

    final_response = result.get("output", "")
    image_url = None

    for action, observation in result.get("intermediate_steps", []):
        if action.tool == "WatchTool":
            if isinstance(observation, dict):
                image_url = observation.get("image_url")

    return final_response, image_url
