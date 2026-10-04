from database import get_session, Task
from fastapi import APIRouter, HTTPException, Depends
from models import TaskOut
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/", response_model=list[TaskOut])
async def get_done(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Task).where(Task.status == "done"))
    return result.scalars().all()


@router.get("/{task_id}", response_model=TaskOut)
async def get_task_done(task_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.status == "done")
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="Task not found"
        )
    return task


@router.post("/{task_id}", response_model=TaskOut)
async def move_to_done(task_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="Task not found"
        )

    if task.status != "in_work":
        raise HTTPException(
            status_code=400,
            detail="Task is not in 'in_work'. Only in_work tasks can be moved to done."
        )

    task.status = "done"
    await session.commit()
    await session.refresh(task)
    return task


@router.delete("/{task_id}")
async def delete_task_done(task_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.status == "done")
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
