from dotenv import load_dotenv
import os
from typing import Optional
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_qwq import ChatQwen
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate
)

from src.agents.memory_manager.chat_memory_history import AIMemoryManager
from src.tools.watch_tool import find_and_download_watch
import getpass
import os

if not os.getenv("DASHSCOPE_API_KEY"):
    os.environ["DASHSCOPE_API_KEY"] = getpass.getpass("Enter your Dashscope API key: ")

load_dotenv()

llm = ChatQwen(
    model="qwen3-max",
    temperature=0.2,
    reasoning_effort='high'
)


class StructuredMainOutput(BaseModel):
    response: str = Field(description="Response for the user")
    image_url: Optional[str] = Field(
        description="Image URL if watch found",
        default=None
    )


def main_agent_invoke(sessionid: str, message: str, OCR_message: str):
    """
    Main agent with proper tool integration.
    First tries to use tools, then formats response.
    """
    
    # Load system prompt
    main_prompt_path = os.getenv("main_prompt")
    with open(main_prompt_path, "r", encoding="utf-8") as f:
        system_prompt_text = f.read()

    memory = AIMemoryManager(sessionid)
    chat_history = memory.get_conversation_buffer_memory()

    # System prompt
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
        
        TOOL USAGE:
        - If you have enough info about the watch model, USE the find_and_download_watch tool
        - The tool will search inventory and return an image if available
        - Only use the tool when you know the specific model/reference
        
        Keep responses short and WhatsApp-casual
        Ask ONLY ONE question
        Never mention tools, databases, or being AI
        No markdown, no emojis
        """
    )

    prompt = ChatPromptTemplate.from_messages([
        system_prompt,
        human_prompt
    ])

    # Step 1: Agent WITH tools (can make tool calls)
    agent_with_tools = prompt | llm.bind_tools([find_and_download_watch])

    # Invoke with tool capability
    input_data = {
        "chat_history": chat_history,
        "last_message": message,
        "ocr_text": OCR_message,
        "watch_name": "",
        "budget": "",
        "message_type": "text",
        "purchase_time": ""
    }
    
    print("🤖 Invoking agent with tools...")
    result = agent_with_tools.invoke(input_data)
    
    # Step 2: Check if tool was called
    image_url = None
    final_response = None
    
    if hasattr(result, 'tool_calls') and result.tool_calls:
        print(f"🔧 Tool called: {len(result.tool_calls)} tool(s)")
        
        # Execute each tool call
        for tool_call in result.tool_calls:
            print(f"   Tool: {tool_call['name']}")
            print(f"   Args: {tool_call['args']}")
            
            if tool_call['name'] == 'find_and_download_watch':
                # Execute the tool
                tool_result = find_and_download_watch.invoke(tool_call['args'])
                print(f"   Result: {tool_result}")
                
                # Extract image URL if present
                if isinstance(tool_result, dict) and 'image_url' in tool_result:
                    image_url = tool_result['image_url']
                elif isinstance(tool_result, str):
                    # Tool might return URL directly or message
                    if tool_result.startswith('http'):
                        image_url = tool_result
        
        # Step 3: Generate response WITH tool results
        print("💬 Generating response with tool results...")
        
        response_prompt = ChatPromptTemplate.from_messages([
            system_prompt,
            HumanMessagePromptTemplate.from_template(
                """
                CONVERSATION HISTORY
                {chat_history}

                USER MESSAGE
                {last_message}

                TOOL RESULTS
                Image URL: {tool_image_url}
                
                Generate a natural response mentioning you found the watch.
                Keep it short and casual.
                Don't mention using tools or database.
                """
            )
        ])
        
        response_agent = response_prompt | llm.with_structured_output(StructuredMainOutput)
        
        structured_result = response_agent.invoke({
            "chat_history": chat_history,
            "last_message": message,
            "tool_image_url": image_url or "Not found"
        })
        
        final_response = structured_result.response
        if image_url is None:
            image_url = structured_result.image_url
    
    else:
        print("❌ No tools called - generating conversational response")
        # No tool call, just use the content
        if hasattr(result, 'content'):
            final_response = result.content
        else:
            final_response = str(result)
    
    # Save to memory
    memory.add_message("human", message)
    memory.add_message("ai", final_response)
    
    print(f"📤 Response: {final_response}")
    print(f"🖼️  Image URL: {image_url}")
    
    return final_response, image_url