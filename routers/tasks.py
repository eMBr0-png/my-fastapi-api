from database import tasks
import database
from fastapi import APIRouter, HTTPException
from models import Task, TaskUpdate

router = APIRouter()

@router.get("/")
async def get_all_tasks():
    return tasks

@router.get("/{task_id}")
async def get_one_task(task_id: int):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="Task not found"
        )
    return task

@router.post("/", status_code=201)
async def create_task(task: Task):
    global next_id

    for existing in tasks:
        if existing["title"] == task.title:
            raise HTTPException(
                status_code=400,
                detail="This task is already saved in tasks"
            )
    
    new_task = {
        "id": database.next_id,
        "title": task.title,
        "description": task.description,
        "status": "todo"
    }
    tasks.append(new_task)
    database.next_id += 1
    return new_task

@router.put("/{task_id}")
async def edit_task(task_id: int, task_update: TaskUpdate):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    update_data = task_update.model_dump(exclude_unset=True)

    forbidden = {"id", "status"}
    if forbidden & update_data.keys():
        raise HTTPException(
            status_code=400,
            detail="Fields 'id' and 'status' are read-only"
        )

    if "title" in update_data:
        for existing in tasks:
            if existing["id"] != task_id and existing["title"] == update_data["title"]:
                raise HTTPException(
                    status_code=400,
                    detail="Task with this title already exists"
                )
    
    task.update(update_data)
    return task

@router.delete("/{task_id}")
async def delete_task(task_id: int):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="Task not found"
        )
    
    tasks.remove(task)
    return task
