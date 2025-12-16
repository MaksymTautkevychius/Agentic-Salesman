from langchain_community.utilities import SQLDatabase
from langchain.tools import tool
from langchain_community.agent_toolkits import create_sql_agent
from langchain_anthropic import ChatAnthropic
import time, re, os, requests
from dotenv import load_dotenv

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
@tool('WatchTool')
def find_and_download_watch(message: str):
    """
    Find the best matching watch and download its image to memory
    Returns the image as bytes along with watch details
    """
    search_text = message
    
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
    Find the SINGLE BEST matching watch in the watches table for: {search_text}
    
    {prompt_text}
    """
    
    try:
        response = agent.invoke({"input": query})
        result_text = response["output"]
        
        print("Search Results:")
        print(result_text)
        print("\n" + "="*60 + "\n")
        
        url_match = re.search(r'(https?://[^\s,\)\]]+\.(?:png|jpg|jpeg|webp))', 
                            result_text, re.IGNORECASE)
        
        if url_match:
            image_url = url_match.group(1)
            
            img_response = requests.get(image_url, timeout=15)
            img_response.raise_for_status()
            
            return {
                "success": True,
                "watch_details": result_text,
                "image_url": image_url
            }
        else:
            return {
                "success": False,
                "watch_details": result_text,
                "error": "Found watch but no image URL in database"
            }
            
    except Exception as e:
        return {
            "success": False,
            "image_data": None,
            "error": f"Search failed: {str(e)}",
            "criteria": search_text
        }

if __name__ == "__main__":
    print("Example 1: RM")
    start = time.time()
    result = find_and_download_watch("126613LN blk gold & steel (2 pis) 68,500 AED")
    elapsed = time.time() - start
    
    print(f"\nResult: {result}")
    print(f"Search time: {elapsed:.2f} seconds\n")
    
    if result.get("success") and result.get("image_data"):
        with open("RM.jpg", "wb") as f:
            f.write(result["image_data"])
        print("Image saved to RM.jpg")
    
    print("="*60 + "\n")