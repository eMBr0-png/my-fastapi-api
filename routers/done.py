import database
from database import done
from fastapi import APIRouter, HTTPException
from models import Task, TaskUpdate

router = APIRouter()

@router.get("/")
async def get_done():
    return done

@router.post("/{task_id}")
async def move_to_done(task_id: int):
    task = next((t for t in in_work if t["id"] == task_id), None)
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="Task not found. Maybe it is still in tasks? Try again"
        )

    task["status"] = "done"
    done.append(task)
    in_work.remove(task)
    return task

@router.delete("/{task_id}")
async def delete_task_done(task_id: int):
    task = next((t for t in done if t["id"] == task_id), None)
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="Task not found"
        )
    
    done.remove(task)
    return task
