from fastapi import FastAPI, HTTPException, Depends

from todo.database.schema import Todo
from todo.database.database_tables import create_tables
from todo.models.models import TodoCreate

from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from todo.database.database_connectivity import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables..")
    create_tables()
    yield

app: FastAPI = FastAPI(lifespan=lifespan, title="TodoAPI with sqlmodel",
                       version="0.0.1",
                       servers=[
                        {
                            "url": "http://127.0.0.1:8000", # ADD NGROK URL Here Before Creating GPT Action
                            "description": "Development Server"
                        }
                        ])

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
]

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


def get_db():
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()


@app.get("/todos/")
def read_todos(db: Session = Depends(get_db)):
    todo = db.exec(select(Todo)).all()
    return todo

# get todo by id
@app.get("/todos/{todo_id}")
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.get(Todo, todo_id)  # Use SQLModel's get method for retrieving by primary key
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.post("/todos/")
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = Todo(title=todo.title, description=todo.description)
    db.add(db_todo)  # Add the new Todo object to the session
    db.commit()  # Commit the transaction
    db.refresh(db_todo)  # Refresh the instance with new data from the database
    return db_todo

@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, updated_todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = db.get(Todo, todo_id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db_todo.title = updated_todo.title
    db_todo.description = updated_todo.description
    db.commit()
    return db_todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.get(Todo, todo_id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(db_todo)
    db.commit()
    return {"message": "Todo deleted"}