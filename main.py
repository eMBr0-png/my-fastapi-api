from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Task(BaseModel):
    title: str
    description: str = ""

tasks: List[dict] = []
in_work: List[dict] = []
done: List[dict] = []
next_id = 1

@app.get("/tasks")
async def get_all_tasks():
    return tasks

@app.post("/tasks")
async def create_task(task: Task):
    global next_id

    for existing in tasks:
        if existing["title"] == task.title:
            raise HTTPException(
                status_code=400,
                detail="This task is already saved in tasks"
            )
    new_task = {
        "id": next_id,
        "title": task.title,
        "description": task.description,
        "status": "todo"
    }
    tasks.append(new_task)
    next_id += 1
    return new_task

@app.get("/in_work")
async def get_in_work():
    return in_work

@app.post("/in_work/{task_id}")
async def move_to_in_work(task_id: int):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if any(t["id"] == task_id for t in in_work):
        return {"message": "Already in work"}

    task["status"] = "in_work"
    in_work.append(task)
    return task

@app.get("/done")
async def get_done():
    return done

@app.post("/done/{task_id}")
async def move_to_done(task_id: int):
    task = next((t for t in in_work if t["id"] == task_id), None)
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="This task is not found in in_work. Maybe it is still in tasks? Try again")

    task["status"] = "done"
    done.append(task)
    return task
