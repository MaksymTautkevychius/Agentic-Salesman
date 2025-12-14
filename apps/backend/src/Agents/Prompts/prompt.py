import os
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate,ChatPromptTemplate

"""
THIS PART OF CODE WILL BE DELETED, ALL PROMPT FILES WILL BE ADDED TO THE .giignore FILES AND DOWNLOADED IN THE .py FILES OF ITS FUNCTION
"""

system_prompt = SystemMessagePromptTemplate.from_template(
    os.getenv('main_prompt')
)
user_prompt= HumanMessagePromptTemplate.from_template(
"""
CONVERSATION CONTEXT
**User's Last Message:** {last_message}

EXTRACTED INFORMATION
Watch Name/Details: {watch_name}
Budget Mentioned: {budget}
Message Type: {message_type}
Purchase Timing: {purchase_time}


RESPONSE REQUIREMENTS
Respond as Adam using the System Prompt rules
Follow the flow sequence (0→1→2→3→4) based on current state
Use the extracted information above to determine next action
If Watch Name is incomplete or unclear, start at step 0
If Watch Name is complete, proceed to appropriate flow step
Match message style to Type (text/image)
Consider Purchase Timing for deposit logic

CRITICAL REMINDERS
Ask ONLY ONE question per response
Keep it short and WhatsApp-casual
Never mention tools, databases, or being AI
Use exact template wording on first use
Paraphrase on repeat questions
No markdown, no formatting, no emojis
Don't start with "Got it", "Sure", "Okay", etc.

NEXT ACTION
Based on the above information, determine:
1. Which flow step applies?
2. What information is missing?
3. What's the single best question or response right now?


""",
input_variables=["last_message","watch_name", "budget", "message_type", "purchase_time"]
)
main_agent_prompt = ChatPromptTemplate.from_messages([
    system_prompt,
    user_prompt
])

image_OCR_prompt = os.getenv('image_handler_prompt')