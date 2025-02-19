import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from main import app
from models import Base

DATABASE_URL = "sqlite+aiosqlite:///./test_recipes.db"
engine = create_async_engine(DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


@pytest.fixture
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            yield session
            await session.rollback()
    await engine.dispose()


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    return TestClient(app)


async def get_db():
    async with TestingSessionLocal() as session:
        yield session


async def create_test_recipe(client):
    return client.post(
        "/recipes/",
        json={
            "name": "Test Recipe",
            "cooking_time": 30,
            "ingredients": "Test Ingredients",
            "description": "Test Description",
        },
    )


@pytest.mark.asyncio
async def test_create_recipe(client):
    response = await create_test_recipe(client)
    assert response.status_code == 200
    assert "id" in response.json()


@pytest.mark.asyncio
async def test_get_recipes(client):
    await create_test_recipe(client)
    response = client.get("/recipes/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_recipe(client):
    create_response = await create_test_recipe(client)
    recipe_id = create_response.json()["id"]

    response = client.get(f"/recipes/{recipe_id}")
    assert response.status_code == 200
    assert response.json()["id"] == recipe_id


@pytest.mark.asyncio
async def test_get_nonexistent_recipe(client):
    response = client.get("/recipes/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Recipe not found"
