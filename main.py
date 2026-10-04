from fastapi import FastAPI
from routers.tasks import router as tasks_router
from routers.in_work import router as in_work_router
from routers.done import router as done_router
from contextlib import asynccontextmanager
from database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
app.include_router(in_work_router, prefix="/in_work", tags=["in_work"])
app.include_router(done_router, prefix="/done", tags=["done"])
