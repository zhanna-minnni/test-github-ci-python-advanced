from typing import Annotated, List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import update
from sqlalchemy.future import select

from database import async_session, engine
from models import Base, Recipe as RecipeModel
from schemas import Recipe as RecipeSchema, RecipeCreate

app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()


async def get_db():
    async with async_session() as session:
        yield session


@app.post("/recipes/", response_model=RecipeSchema)
async def create_recipe(recipe: RecipeCreate, db: AsyncSession = Depends(get_db)):
    new_recipe = RecipeModel(**recipe.model_dump())
    db.add(new_recipe)
    await db.commit()
    await db.refresh(new_recipe)
    return new_recipe


@app.get("/recipes/", response_model=List[RecipeSchema])
async def get_recipes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RecipeModel).order_by(RecipeModel.views.desc(), RecipeModel.cooking_time)
    )
    return result.scalars().all()


@app.get("/recipes/{recipe_id}", response_model=RecipeSchema)
async def get_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    await db.execute(
        update(RecipeModel.__table__)
        .where(RecipeModel.id == recipe_id)
        .values(views=RecipeModel.views + 1)
    )
    await db.commit()

    result = await db.execute(select(RecipeModel).where(RecipeModel.id == recipe_id))
    recipe = result.scalars().first()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe
