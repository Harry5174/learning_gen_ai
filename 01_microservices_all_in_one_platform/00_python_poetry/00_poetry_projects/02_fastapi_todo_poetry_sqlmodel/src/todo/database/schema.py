from sqlmodel import Field, SQLModel 

class Todo(SQLModel, table=True):
    __tablename__ = 'todos'

    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str