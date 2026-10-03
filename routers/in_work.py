import database
from database import in_work
from fastapi import APIRouter, HTTPException
from models import Task, TaskUpdate

router = APIRouter()

@router.get("/")
async def get_in_work():
    return in_work

@router.get("/{task_id}")
async def get_task_in_work(task_id: int):
    task = next((t for t in in_work if t["id"] == task_id), None)
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="Task not found"
        )
    return task

@router.post("/{task_id}")
async def move_to_in_work(task_id: int):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="Task not found"
        )

    if any(t["id"] == task_id for t in in_work):
        return {"message": "Already in work"}

    task["status"] = "in_work"
    in_work.append(task)
    tasks.remove(task)
    return task

@router.delete("/{task_id}")
async def delete_task_in_work(task_id: int):
    task = next((t for t in in_work if t["id"] == task_id), None)
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="Task not found"
        )
    
    in_work.remove(task)
    return task
