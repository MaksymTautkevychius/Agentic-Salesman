import json

ai_msg = '''
{
    "role": "assistant",
    "content": "Hello, how can I help you?"
}
'''

# Convert string → Python dict
ai_msg_obj = json.loads(ai_msg)

print(ai_msg_obj)
# {'role': 'assistant', 'content': 'Hello, how can I help you?'}
print(type(ai_msg_obj))
# <class 'dict'>