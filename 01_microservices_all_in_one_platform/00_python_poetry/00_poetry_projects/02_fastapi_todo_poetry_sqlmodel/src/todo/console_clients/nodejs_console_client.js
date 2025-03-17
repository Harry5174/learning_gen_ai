"use strict";
// nodejs_console_client.ts
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const axios_1 = __importDefault(require("axios"));
const BASE_URL = "http://127.0.0.1:8000";
function getTodos() {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            const response = yield axios_1.default.get(`${BASE_URL}/todos`);
            console.log("Todos were successfully retrieved:");
            console.log(response.data);
        }
        catch (error) {
            console.log({ "Error (getTodo) ": error.message });
        }
    });
}
function getTodo(id) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            const response = yield axios_1.default.get(`${BASE_URL}/todos/${id}`);
            console.log("Todo was successfully retrieved:");
            console.log(response.data);
        }
        catch (error) {
            console.log({ "Error (getTodo) ": error.message });
        }
    });
}
function createTodo(todo) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            yield axios_1.default.post(`${BASE_URL}/todos/`, {
                title: todo.title,
                description: todo.description,
            });
            console.log("Todo added successfully");
        }
        catch (error) {
            console.error("Error (createTodo) :", error.message);
        }
    });
}
function updateTodo(id, todo) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            yield axios_1.default.put(`${BASE_URL}/todos/${id}`, {
                title: todo.title,
                description: todo.description,
            });
            console.log("updated todo successfully");
        }
        catch (error) {
            console.log("Error (updatedTodo) :", error.message);
        }
    });
}
function deleteTodo(id) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            const response = yield axios_1.default.delete(`${BASE_URL}/todos/${id}`);
            console.log("Todo deleted successfully");
        }
        catch (error) {
            console.error("Error (deleteTodo) :", error.message);
        }
    });
}
let todoCreate = {
    title: "test todo",
    description: "test todo's description",
};
let todoUpdate = {
    title: "updated todo",
    description: "updated todo's description",
};
// createTodo(todoCreate);
getTodos();
// deleteTodo(2);
// getTodo(5);
// updateTodo(5, todoUpdate);
// getTodos();
