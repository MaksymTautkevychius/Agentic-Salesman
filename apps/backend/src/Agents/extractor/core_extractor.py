from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.agents.extractor.core_extractor_class import CoreExtractor
from langchain_core.output_parsers import PydanticOutputParser

def extract_data(message: str, OCR_message: str)-> object:
    """
    Extracts parameters defined in the given class
    """
    model = ChatOpenAI(model="gpt-4.1")
    parser = PydanticOutputParser(pydantic_object=CoreExtractor)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Extract structured information from the user message."),
        ("human", "{input_text}"),
        ("system", "Return the result in JSON format: {format_instructions}")
    ]).partial(format_instructions=parser.get_format_instructions())
    chain = prompt | model | parser
    CoreExtractor = chain.invoke({"input_text": f"text message:{message}, product_on_image:{OCR_message}, chat_history:"})
    return 
