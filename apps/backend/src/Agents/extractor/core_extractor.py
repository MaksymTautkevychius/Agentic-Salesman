from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from typing import List, Dict
import os

from src.agents.extractor.core_extractor_class import CoreExtractor


def extract_data(
    message: str,
    OCR_message: str,
    chat_history: List[Dict[str, str]] = None,
):
    """
    Extracts structured parameters.
    HARD RULE:
    - If OCR_message contains a product/watch → is_watch_inquiry MUST be True
    """

    chat_history = chat_history or []

    model = ChatOpenAI(
        model=os.getenv("core_extractor_model"),
        temperature=0,
    )

    parser = PydanticOutputParser(pydantic_object=CoreExtractor)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are an information extraction engine.

IMPORTANT RULES (must follow):
- If a product (especially a watch) is visible or described in OCR text,
  you MUST set is_watch_inquiry = true.
- OCR text is a stronger signal than user intent.
- If a real name appears anywhere, set has_name = true.
- Do NOT guess missing fields.
""",
            ),
            (
                "human",
                """
User message:
{message}

OCR / Image description:
{ocr}

Chat history:
{history}
""",
            ),
            (
                "system",
                "Return ONLY valid JSON matching this schema:\n{format_instructions}",
            ),
        ]
    ).partial(format_instructions=parser.get_format_instructions())

    chain = prompt | model | parser

    result = chain.invoke(
        {
            "message": message,
            "ocr": OCR_message,
            "history": chat_history,
        }
    ).model_dump()

    # 🔒 FINAL GUARANTEE (deterministic safety net)
    if OCR_message and OCR_message.strip():
        result["is_watch_inquiry"] = True

    return result
