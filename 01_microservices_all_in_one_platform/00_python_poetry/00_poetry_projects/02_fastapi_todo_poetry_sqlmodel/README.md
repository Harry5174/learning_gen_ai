Copy code

# FastAPI Todo Backend

This FastAPI backend provides RESTful APIs for managing todo items stored in a database. It includes console client modules in both Node.js and Python for interacting with the backend APIs.

## Description

This project serves as the backend for a todo application. It exposes endpoints for CRUD operations on todo items, including listing all todos, adding new ones, updating existing ones, and deleting them. SQLModel is used for interacting with the database.

## Modules

The backend consists of the following modules:

- `console_clients`: Contains console client modules for interacting with the backend APIs.
- `database`: Contains modules related to database connectivity and schema definition using SQLModel.
- `models`: Contains Pydantic models for defining the structure of todo items.
- `routes`: Contains FastAPI routes for handling HTTP requests.
- `streamlit`: Contains a Streamlit web interface for user interaction with the backend.

## Clone and Run

To clone and run the project, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/Harry5174/learning_generative_ai.git
   cd learning_generative_ai/01_microservices_all_in_one_platform/00_python_poetry/00_poetry_projects/02_fastapi_todo_poetry_sqlmodel
   ```
Install Python Poetry if you haven't already...

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

Install project dependencies using Poetry:
```bash
poetry install
```
Start the FastAPI server:

bash
Copy code:

```bash
poetry run uvicorn todo.main:app --reload
```

Run the Streamlit app:

```bash
streamlit run todo.streamlit.streamlit_client.py
```

# API Reference
The backend exposes the following API endpoints:

- **GET /todos:** Retrieves all todo items.
- **GET /todos/{id}:** Retrieves a specific todo item by its ID.
- **POST /todos/:** Creates a new todo item.
- **PUT /todos/{id}:** Updates an existing todo item.
- **DELETE /todos/{id}:** Deletes a todo item by its ID.

# Database
The database module contains modules for database connectivity and schema definition using SQLModel:

- **database_connectivity.py:** Establishes database connectivity.
- **database_tables.py:** Defines database tables and creates them if they do not exist.
- **schema.py:** Defines the schema for todo items using SQLModel.

# Contributing
Contributions are welcome! Follow these steps to contribute to the project:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/improvement`).
3. Make your changes and commit them (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/improvement`).
5. Create a new Pull Request.

# License
This project is licensed under the MIT License.

# Contact Information
For questions or suggestions, please contact [harisjaved010@gmail.com](mailto:harisjaved010@gmail.com).

