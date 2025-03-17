# type: ignore

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel 
from todo.database.database_connectivity import SessionLocal
from todo.database.models import Todo
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.sql import select

class TodoCreate(BaseModel):
    title: str
    description: str

app: FastAPI = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000/api/todo",
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
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/todos/")
def read_todos(db: Session = Depends(get_db)):
        
    todos = db.execute(select(Todo)).scalars().all()
    return todos

# get todo by id
@app.get("/todos/{todo_id}") 
def read_todos(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo 


@app.post("/todos/")
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    print(f"Received request to create todo: {todo}")
    db_todo = Todo(title=todo.title, description=todo.description)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, updated_todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    for key, value in updated_todo.model_dump().items():
        setattr(db_todo, key, value)
    db.commit()
    return db_todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(db_todo)
    db.commit()
    return {"message": "Todo deleted"}