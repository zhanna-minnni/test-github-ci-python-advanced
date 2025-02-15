from fastapi import FastAPI
from sqlalchemy.future import select
from sqlalchemy import update
from typing import List
from models import Base, Recipe as RecipeModel
from schemas import RecipeCreate, Recipe as RecipeSchema
from database import engine, async_session


app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()


@app.post("/recipes/", response_model=RecipeSchema)
async def create_recipe(recipe: RecipeCreate):
    async with async_session() as session:
        new_recipe = RecipeModel(**recipe.model_dump())
        session.add(new_recipe)
        await session.commit()
        await session.refresh(new_recipe)
        return new_recipe


@app.get("/recipes/", response_model=List[RecipeSchema])
async def get_recipes():
    async with async_session() as session:
        result = await session.execute(
            select(RecipeModel).order_by(
                RecipeModel.views.desc(), RecipeModel.cooking_time
            )
        )
        return result.scalars().all()
        

@app.get("/recipes/{recipe_id}", response_model=RecipeSchema)
async def get_recipe(recipe_id: int):
    async with async_session() as session:
        await session.execute(
            update(RecipeModel)
            .where(RecipeModel.id == recipe_id)
            .values(views=RecipeModel.views + 1)
        )

        result = await session.execute(
            select(RecipeModel).where(RecipeModel.id == recipe_id)
        )
        recipe = result.scalars().first()

        return recipe
