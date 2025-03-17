import requests # type: ignore
import json  # Import the json module
from pydantic import BaseModel

BASE_URL = "http://127.0.0.1:8000"

def get_todos():
    response = requests.get(f"{BASE_URL}/todos")
    if response.status_code == 200:
        print("Todos were retrieved successfully!")
        todos = json.loads(response.content)
        for todo in todos:
            print(f"ID: {todo['id']}")
            print(f"Title: {todo['title']}")
            print(f"Description: {todo['description']}")
            print()
    else:
        print("Failed to retrieve todos.")

def create_todo():
    title = input("Enter Todo Title: ")
    description = input("Enter Todo Description: ")
    response = requests.post(f"{BASE_URL}/todos/", json={"title": title, "description": description})
    if response.status_code == 200:
        print("Todo added successfully")
    else:
        print("Failed to add todo.")

def update_todo():
    id = input("Enter the id of the todo you want to update: ")
    title = input("Enter Todo Title to update: ")
    description = input("Enter Todo Description to update: ")
    response = requests.put(f"{BASE_URL}/todos/{id}", json={"title": title, "description": description})
    if response.status_code == 200:
        print("Todo updated successfully")
    else: 
        print("update failed!")

def delete_todo():
    todo_id = input("Enter Todo ID to delete: ")
    response = requests.delete(f"{BASE_URL}/todos/{todo_id}")
    if response.status_code == 200:
        print("Todo deleted successfully")
    else:
        print("Failed to delete todo.")

if __name__ == "__main__":
    get_todos()
    # update_todo()
    # get_todos()
    # create_todo()
    # delete_todo()
