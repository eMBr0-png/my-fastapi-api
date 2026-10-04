from pydantic import BaseModel
from typing import Optional

class TaskCreate(BaseModel):
    title: str
    description: str = ""

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    status: str

    model_config = {"from_attributes": True}