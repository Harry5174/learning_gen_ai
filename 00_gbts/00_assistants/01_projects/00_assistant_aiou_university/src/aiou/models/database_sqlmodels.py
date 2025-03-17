from sqlmodel import SQLModel, Field
from datetime import datetime

# Database model for logging queries and responses
class QueryLog(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_query: str
    assistant_response: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)