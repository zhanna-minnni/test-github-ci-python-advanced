from typing import List

from fastapi import FastAPI, HTTPException
from sqlalchemy import update
from sqlalchemy.future import select

from database import async_session, engine
from models import Base
from models import Recipe as RecipeModel
from schemas import Recipe as RecipeSchema
from schemas import RecipeCreate

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
            update(RecipeModel.__table__)
            .where(RecipeModel.id == recipe_id)
            .values(views=RecipeModel.views + 1)
        )
        await session.commit()

        result = await session.execute(
            select(RecipeModel).where(RecipeModel.id == recipe_id)
        )
        recipe = result.scalars().first()
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return recipe
