from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import os
from src.agents.extractor.core_extractor_class import CoreExtractor 
from typing import List,Dict

def extract_data(message: str, OCR_message: str, chat_history:List[Dict[str, str]]  = "") : 
    """
    Extracts parameters defined in the given class
    """
    model = ChatOpenAI(model=os.getenv('core_extractor_model'))
    parser = PydanticOutputParser(pydantic_object=CoreExtractor)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Extract structured information from the user message."),
        ("human", "{input_text}"),
        ("system", "Return the result in JSON format: {format_instructions}")
    ]).partial(format_instructions=parser.get_format_instructions())
    chain = prompt | model | parser
    result = chain.invoke({"input_text": f"text message:{message}, product_on_image:{OCR_message}, chat_history:{chat_history}"})
    return result.model_dump() 

def test_extract_data():
    """
    Test method to verify extract_data function with example data
    """
    print("=" * 50)
    print("Testing extract_data function...")
    print("=" * 50)
    
    # Example data
    message = "I want to buy 2 black iPhones with 256GB storage"
    
    ocr_message = "iPhone 15 Pro - $999.99 - Available in Black, Silver, Gold"
    
    chat_history = [
        {
            "role": "user",
            "content": "Hello, I'm looking for a new phone"
        },
        {
            "role": "assistant",
            "content": "Hello! I'd be happy to help you find a phone. What features are you looking for?"
        },
        {
            "role": "user",
            "content": "I need something with good storage and camera"
        },
        {
            "role": "assistant",
            "content": "Great! I recommend checking out the latest iPhone models. They have excellent cameras and storage options."
        }
    ]
    
    try:
        # Call the extract_data function
        print("\nInput Data:")
        print(f"Message: {message}")
        print(f"OCR Message: {ocr_message}")
        print(f"Chat History Length: {len(chat_history)} messages")
        print("\n" + "-" * 50)
        
        result = extract_data(
            message=message,
            OCR_message=ocr_message,
            chat_history=chat_history
        )
        
        print("\nExtraction Result:")
        print("-" * 50)
        for key, value in result.items():
            print(f"{key}: {value}")
        
        print("\n" + "=" * 50)
        print("✓ Test completed successfully!")
        print("=" * 50)
        
        return result
        
    except Exception as e:
        print("\n" + "=" * 50)
        print(f"✗ Test failed with error:")
        print(f"Error: {str(e)}")
        print("=" * 50)
        raise