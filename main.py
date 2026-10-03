from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Task(BaseModel):
    title: str
    description: str = ""

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None

tasks: List[dict] = []
in_work: List[dict] = []
done: List[dict] = []
next_id = 1

@app.get("/tasks")
async def get_all_tasks():
    return tasks

@app.get("/tasks/{task_id}")
async def get_one_task(task_id: int):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="Task not found"
        )
    return task

@app.post("/tasks", status_code=201)
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

@app.put("/tasks/{task_id}")
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

# async def edit_task(task_id: int, element_to_edit: str, edited_text: str):
    # if element_to_edit == "title":
    #     for existing in tasks:
    #         if existing["title"] == edited_text and existing["id"] != task_id:
    #             raise HTTPException(
    #                 status_code=400,
    #                 detail="This task already exists"
    #             )
    
    # editable_elements = "title", "description"
    # match element_to_edit:
    #     case "title":
    #         task["title"] = edited_text
    #     case "description":
    #         task["description"] = edited_text
    #     case "id":
    #         raise HTTPException(
    #             status_code=400,
    #             detail="Bad request. You can not edit id or status of the task"
    #         )
    #     case "status":
    #         raise HTTPException(
    #             status_code=400,
    #             detail="Bad request. You can not edit id or status of the task"
    #         )
    #     case _:
    #         raise HTTPException(
    #             status_code=400,
    #             detail=f"Unknown field '{element_to_edit}'. Editable: {editable_elements}"
    #         )
    # return task

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="Task not found"
        )
    
    tasks.remove(task)
    return task

@app.get("/in_work")
async def get_in_work():
    return in_work

@app.get("/in_work/{task_id}")
async def get_task_in_work(task_id: int):
    task = next((t for t in in_work if t["id"] == task_id), None)
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="Task not found"
        )
    return task

@app.post("/in_work/{task_id}")
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

@app.delete("/in_work/{task_id}")
async def delete_task_in_work(task_id: int):
    task = next((t for t in in_work if t["id"] == task_id), None)
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="Task not found"
        )
    
    in_work.remove(task)
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
            detail="Task not found. Maybe it is still in tasks? Try again"
        )

    task["status"] = "done"
    done.append(task)
    in_work.remove(task)
    return task

@app.delete("/done/{task_id}")
async def delete_task_done(task_id: int):
    task = next((t for t in done if t["id"] == task_id), None)
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="Task not found"
        )
    
    done.remove(task)
    return task
