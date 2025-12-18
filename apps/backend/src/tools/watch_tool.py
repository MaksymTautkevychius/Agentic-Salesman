import os
import re
import requests
from dotenv import load_dotenv

from langchain.tools import tool
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_anthropic import ChatAnthropic

load_dotenv()

USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

db_url = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/postgres"
db = SQLDatabase.from_uri(db_url, include_tables=["watches"])

llm = ChatAnthropic(
    model="claude-sonnet-4-5-20250929",
    temperature=0
)

@tool("WatchTool")
def WatchTool(watch_name: str):
    """
    Find the SINGLE best matching watch and return its image URL if available.
    """

    if not watch_name or not watch_name.strip():
        return {
            "success": False,
            "error": "watch_name is empty"
        }

    agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="zero-shot-react-description",
        verbose=True,
        handle_parsing_errors=True,
    )

    prompt_path = os.getenv("tool_prompt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_text = f.read()

    query = f"""
    Find the SINGLE BEST matching watch in the watches table for:
    {watch_name}

    {prompt_text}
    """

    try:
        response = agent.invoke({"input": query})
        result_text = response.get("output", "")

        url_match = re.search(
            r'(https?://[^\s,\)\]]+\.(?:png|jpg|jpeg|webp))',
            result_text,
            re.IGNORECASE
        )

        if url_match:
            image_url = url_match.group(1)
            return {
                "success": True,
                "watch_details": result_text,
                "image_url": image_url
            }

        return {
            "success": False,
            "watch_details": result_text,
            "error": "No image URL found"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "criteria": watch_name
        }
