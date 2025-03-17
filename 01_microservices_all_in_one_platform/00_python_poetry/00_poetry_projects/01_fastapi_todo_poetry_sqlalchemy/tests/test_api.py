import pytest
from fastapi.testclient import TestClient
from src.todo.routes.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client

@pytest.mark.parametrize(
    "todo_id",
    [
        pytest.param(4, id="Existing Todo ID"),
        pytest.param(100, id="Non-existent Todo ID"),
    ],
)
def test_read_todo_by_id(client, todo_id):
    response = client.get(f"/todos/{todo_id}")
    if response.status_code == 200:
        assert isinstance(response.json(), dict)
        assert "id" in response.json()
        assert "title" in response.json()
        assert "description" in response.json()
    elif response.status_code == 404:
        assert response.json()["detail"] == "Todo not found"
    else:
        assert False, f"Unexpected response status code: {response.status_code}"

def test_create_todo(client):
    todo_data = {"title": "Test Todo", "description": "Test Description"}
    response = client.post("/todos/", json=todo_data)
    assert response.status_code == 200
    assert response.json()["title"] == todo_data["title"]
    assert response.json()["description"] == todo_data["description"]

def test_update_todo(client):
    todo_id = 19
    updated_data = {"title": "Updated Todo", "description": "Updated Description"}
    response = client.put(f"/todos/{todo_id}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["id"] == todo_id
    assert response.json()["title"] == updated_data["title"]
    assert response.json()["description"] == updated_data["description"]

def test_delete_todo(client):
    todo_id = 20
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Todo deleted"

def check_test_id_not_exists(client):
    todo_id = 25
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 404
    assert response.json()["message"] == "not found" 
