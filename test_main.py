from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

@pytest.mark.skip(reason="Skipping the test")
def test_create_recipe() -> None:
    response = client.post(
        "/recipes/",
        json={
            "name": "Test Recipe",
            "cooking_time": 30,
            "ingredients": "Test Ingredients",
            "description": "Test Description",
        },
    )
    assert response.status_code == 200
    assert "id" in response.json()


@pytest.mark.skip(reason="Skipping the test")
def test_get_recipes() -> None:
    response = client.get("/recipes/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_recipe() -> None:
    create_response = client.post(
        "/recipes/",
        json={
            "name": "Test Recipe",
            "cooking_time": 30,
            "ingredients": "Test Ingredients",
            "description": "Test Description",
        },
    )
    recipe_id = create_response.json()["id"]

    response = client.get(f"/recipes/{recipe_id}")
    assert response.status_code == 200
    assert response.json()["id"] == recipe_id


@pytest.mark.skip(reason="Skipping the test")
def test_get_nonexistent_recipe() -> None:
    response = client.get("/recipes/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Recipe not found"
