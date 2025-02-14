from pydantic import BaseModel


class RecipeCreate(BaseModel):
    name: str
    cooking_time: int
    ingredients: str
    description: str


class Recipe(BaseModel):
    id: int
    name: str
    cooking_time: int
    ingredients: str
    description: str
    views: int

    model_config = {"from_attributes": True}
