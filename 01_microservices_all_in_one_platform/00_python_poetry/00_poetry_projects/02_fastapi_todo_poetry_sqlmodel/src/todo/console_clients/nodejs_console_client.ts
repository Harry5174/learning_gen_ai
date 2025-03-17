// nodejs_console_client.ts

import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000";

interface Todo {
  title: string;
  description: string;
}

async function getTodos() {
  try {
    const response = await axios.get(`${BASE_URL}/todos`);
    console.log("Todos were successfully retrieved:");
    console.log(response.data);
  } catch (error: any) {
    console.log({ "Error (getTodo) ": error.message });
  }
}

async function getTodo(id: number) {
  try {
    const response = await axios.get(`${BASE_URL}/todos/${id}`);
    console.log("Todo was successfully retrieved:");
    // console.log(response.data);
  } catch (error: any) {
    console.log({ "Error (getTodo) ": error.message });
  }
}

async function createTodo(todo: Todo) {
  try {
    await axios.post(`${BASE_URL}/todos/`, {
      title: todo.title,
      description: todo.description,
    });
    console.log("Todo added successfully");
  } catch (error: any) {
    console.error("Error (createTodo) :", error.message);
  }
}

async function updateTodo(id: number, todo: Todo) {
  try {
    await axios.put(`${BASE_URL}/todos/${id}`, {
        title: todo.title,
        description: todo.description,  
    });
    console.log("updated todo successfully");
  } catch (error: any) {
    console.log("Error (updatedTodo) :", error.message);
  }
}

async function deleteTodo(id: number) {
  try {
    const response = await axios.delete(`${BASE_URL}/todos/${id}`);
    console.log("Todo deleted successfully");
  } catch (error: any) {
    console.error("Error (deleteTodo) :", error.message);
  }
}

let todoCreate: Todo = {
  title: "test todo",
  description: "test todo's description",
};
let todoUpdate: Todo = {
  title: "updated todo",
  description: "updated todo's description",
};

// createTodo(todoCreate);
getTodos();
// deleteTodo(2);
// getTodo(5);

// updateTodo(5, todoUpdate);
// getTodos();
