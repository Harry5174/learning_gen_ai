from packaging import version
from dotenv import load_dotenv

import os
import openai
# import requests


dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env')
load_dotenv(dotenv_path)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Use getenv to avoid KeyError if variable is not set
def version_check():
    # Check OpenAI version is correct
    required_version = version.parse("1.1.1")
    current_version = version.parse(openai.__version__)
    #check version compatibility
    if current_version < required_version:
        raise ValueError(f"Error: OpenAI version {openai.__version__} is less than the required version 1.1.1")
    else:
        print("OpenAI version is compatible.")
        
        
# def query_mistral(prompt: str):
#     # Set the API endpoint for Ollama
#     url = "http://127.0.0.1:11434/api/generate"
    
#     # Set the headers for the request
#     headers =  {
#         'content' : 'application/json'
#     }
    
#     # Payload to query the Mistral 7B model
#     data = {
#         "model" : "mistral",
#         "prompt" : prompt,
#         "max_tokkens" : 500
#     }
    
#     # Make the request to the local Ollama API
#     response = requests.post(url, headers=headers, json=data)
    
#     # check for valid response
#     if response.status_code == 200:
#         return response.json().get('response', '').strip()
#     else:
#         raise Exception(f"Failed to query Mistral API: {response.text}")