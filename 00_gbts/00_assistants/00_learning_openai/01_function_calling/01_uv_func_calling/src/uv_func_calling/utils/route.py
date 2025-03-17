from fastapi import FastAPI
from openai.model import client
from openai.model_tools import tools
from uv_func_calling.utils.functions import get_weather
import json

app = FastAPI()

@app.route('/api/')
def read():
    return {"message": "This is root!"}

@app.route('/chat/')
def query_llm(query: str):
    messages = [{"role":"user", "content":query}],
    
    completion = client.chat.completions.create(
        model = "gbt-4o",
        messages=messages,
        tools = tools
    )

    tool_call = completion.choices[0].message.tool_calls[0]
    args = json.loads(tool_call.function.arguments)

    result = get_weather(args["latitude"], args["longitude"])
    
    
    messages.append(completion.choices[0].message)  # append model's function call message
    messages.append({                               # append result message
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": str(result)
    })

    completion_2 = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
    )
    
    return {"response": completion_2.choices[0].message.content}