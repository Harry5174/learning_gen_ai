import streamlit as st
import requests #type: ignore
# from ..routes.main import *
from todo.routes.routes import *
from todo.console_clients.python_console_client import get_todos


BASE_URL = "http://127.0.0.1:8000"

st.title("Todo App")

def create_todo_streamlit():
    title = st.text_input("Enter Todo Title")
    description = st.text_area("Enter Todo Description")
    if st.button("Add Todo"):
        response = create_todo(title, description)
        if response.status_code == 200:
            st.success("Todo added successfully")
        else:
            st.error("Failed to add todo.")

def delete_todo_streamlit():
    todo_id = st.number_input("Enter Todo ID to delete")
    if st.button("Delete Todo"):
        response = delete_todo(todo_id)
        if response.status_code == 200:
            st.success("Todo deleted successfully")
        else:
            st.error("Failed to delete todo.")

def update_todo_streamlit():
    todo_id = st.number_input("Enter the ID of the todo you want to update")
    title = st.text_input("Enter Todo Title to update")
    description = st.text_area("Enter Todo Description to update")
    if st.button("Update Todo"):
        response = update_todo(todo_id, title, description)
        if response.status_code == 200:
            st.success("Todo updated successfully")
        else:
            st.error("Failed to update todo.")

def display_todos():
    try:
        todos = get_todos()
        if todos:
            st.write("Todos:")
            for todo in todos:
                st.write(f"ID: {todo['id']}")
                st.write(f"Title: {todo['title']}")
                st.write(f"Description: {todo['description']}")
                st.write("------------------------------")
    except Exception as e:
        st.error(f"Failed to fetch todos: {str(e)}")


def display_all_todos():
    display_todos()

if __name__ == "__main__":
    display_all_todos()
    create_todo_streamlit()
    delete_todo_streamlit()
    update_todo_streamlit()
