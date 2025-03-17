import os

from dotenv import load_dotenv
from typing import Optional
from sqlmodel import create_engine
from sqlalchemy import URL

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env')
load_dotenv(dotenv_path)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Use getenv to avoid KeyError if variable is not set
DATABASE_URL : Optional[str | URL] = os.getenv("DATABASE_URL") # insert your database url here


# Database setup
# Ensure database_url is not None before passing it to create_engine

def create_db_engine():
    if DATABASE_URL is not None:
        engine = create_engine(DATABASE_URL)
        return engine
    else:
        raise ValueError("DATABASE_URL environment variable is not set")
    
