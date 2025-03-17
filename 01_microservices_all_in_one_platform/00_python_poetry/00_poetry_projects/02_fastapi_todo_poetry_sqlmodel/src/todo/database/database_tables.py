from .database_connectivity import engine

from sqlmodel import Session,SQLModel
from sqlalchemy.exc import ProgrammingError

def create_tables():
    with Session(engine) as session:
        try:
            SQLModel.metadata.create_all(engine)
            print("Success!...")
        except ProgrammingError as e:
            if "already exists" in str(e):
                print("Table already exists.")
            else:
                print(f"An error occurred: {e}")
