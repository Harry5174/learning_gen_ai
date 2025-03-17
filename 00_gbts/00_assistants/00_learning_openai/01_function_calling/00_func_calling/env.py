# test.py
# this file is for testing your openai key by checking if it is loading from the .env (file) in your directory properly.
from dotenv import load_dotenv
import os

load_dotenv()

print("Test OPENAI_API_KEY:", os.getenv('OPENAI_API_KEY'))
print("Test databaseUrl:", os.getenv('database_url'))