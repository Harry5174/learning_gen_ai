from .database_connectivity import engine
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError


def create_tables():
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            connection.execute(text("CREATE TABLE IF NOT EXISTS todos (id SERIAL PRIMARY KEY, title VARCHAR(255), description VARCHAR(255))"))
            trans.commit()
            print("Table created successfully.")
        except ProgrammingError as e:
            trans.rollback()
            if "already exists" in str(e):
                print("Table already exists.")
            else:
                print(f"An error occurred: {e}")
