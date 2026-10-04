from database import get_session, Task
from fastapi import APIRouter, HTTPException, Depends
from models import TaskCreate, TaskUpdate, TaskOut
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/", response_model=list[TaskOut])
async def get_all_tasks(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Task).where(Task.status == "todo"))
    return result.scalars().all()


@router.get("/{task_id}", response_model=TaskOut)
async def get_one_task(task_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.status == "todo")
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="Task not found"
        )
    return task


@router.post("/", status_code=201, response_model=TaskOut)
async def create_task(task: TaskCreate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Task).where(Task.title == task.title))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="This task is already saved in tasks"
        )
    new_task = Task(title=task.title, description=task.description, status="todo")
    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)
    return TaskOut.model_validate(new_task)


@router.put("/{task_id}", response_model=TaskOut)
async def edit_task(task_id: int, task_update: TaskUpdate,
                    session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="Task not found"
        )

    update_data = task_update.model_dump(exclude_unset=True)

    if "title" in update_data and update_data["title"] != task.title:
        dup = await session.execute(
            select(Task).where(
                Task.title == update_data["title"],
                Task.id != task_id,
            )
        )
        if dup.scalar_one_or_none():
            raise HTTPException(
                status_code=400, 
                detail="Task with this title already exists"
            )

    for field, value in update_data.items():
        setattr(task, field, value)
    await session.commit()
    await session.refresh(task)
    return task


@router.delete("/{task_id}")
async def delete_task(task_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.status == "todo")
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="Task not found"
        )
    await session.delete(task)
    await session.commit()
    return {"ok": True, "id": task_id}
