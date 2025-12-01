from dotenv import load_dotenv 
import os
from Prompts.prompt import main_agent_prompt

OpenAPI = os.getenv('OPEN_API_KEY')
os.environ["OPEN_API_KEY"]= OpenAPI
openai_gpt5 = 'gpt-5'
openai_gpt4_1='gpt-4.1'
openai_gpt5mini='gpt-5-mini'
alibaba_qwen_3max='qwen3-max'




