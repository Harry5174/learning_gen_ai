import os
from dotenv import load_dotenv
from sqlmodel import create_engine

# Loaded environment variables from .env file in the root directory
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env')
load_dotenv(dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)