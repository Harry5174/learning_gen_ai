import pytest
from fastapi.testclient import TestClient
from todo.routes.routes import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client

def test_read_todo_by_id(client):
    existing_todo_id = 1
    response = client.get(f"/todos/{existing_todo_id}")
    if response.status_code == 200:
        assert isinstance(response.json(), dict)
        assert "id" in response.json()
        assert "title" in response.json()
        assert "description" in response.json()
    elif response.status_code == 404:
        assert response.json()["detail"] == "Todo not found"
    else:
        assert False, f"Unexpected response status code: {response.status_code}"

    non_existent_todo_id = 100
    response = client.get(f"/todos/{non_existent_todo_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"

def test_create_todo(client):
    todo_data = {"title": "Test Todo", "description": "Test Description"}
    response = client.post("/todos/", json=todo_data)
    assert response.status_code == 200
    assert response.json()["title"] == todo_data["title"]
    assert response.json()["description"] == todo_data["description"]

def test_update_todo(client):
    existing_todo_id = 2
    updated_data = {"title": "Updated Todo", "description": "Updated Description"}
    response = client.put(f"/todos/{existing_todo_id}", json=updated_data)
    assert response.status_code == 200

def test_delete_todo(client):
    existing_todo_id = 2
    response = client.delete(f"/todos/{existing_todo_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Todo deleted"

