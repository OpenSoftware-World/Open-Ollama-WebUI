from ollama import ChatResponse, chat
def load_model(model_name, msg):
    messages = [
        {
            "role": "user",
            "content": msg
        },
    ]
    response: ChatResponse = chat(model=model_name, messages=messages)
    return response.message.content
