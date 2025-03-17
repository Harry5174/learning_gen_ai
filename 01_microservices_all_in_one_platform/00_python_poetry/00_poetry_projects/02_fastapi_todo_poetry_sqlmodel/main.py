# main.py

# Import statements for modules within the project
from todo.database.database_tables import create_tables
from todo.routes.routes import app

if __name__ == "__main__":
    # Create database tables before running the app
    create_tables()
    
    # Run the FastAPI app
    import uvicorn 
    uvicorn.run(app, host="0.0.0.0", port=8000)
