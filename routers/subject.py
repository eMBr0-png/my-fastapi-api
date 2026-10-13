from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_session, Subject
from models import SubjectCreate, SubjectUpdate, SubjectOut, SubjectWithTasksOut
from typing import List

router = APIRouter(
    prefix="/subjects",
    tags=["subjects"],
)

@router.post("/", response_model=SubjectOut, status_code=status.HTTP_201_CREATED)
async def create_subject(subject: SubjectCreate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Subject).where(Subject.name == subject.name))
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="Subject already exists"
        )
    db_subject = Subject(name=subject.name)
    session.add(db_subject)
    await session.commit()
    await session.refresh(db_subject)
    return db_subject

@router.get("/", response_model=List[SubjectOut])
async def read_subjects(skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Subject).offset(skip).limit(limit))
    subjects = result.scalars().all()
    return subjects

@router.get("/{subject_id}", response_model=SubjectWithTasksOut)
async def read_subject(subject_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Subject).where(Subject.id == subject_id))
    subject = result.scalar_one_or_none()
    
    if subject is None:
        raise HTTPException(
            status_code=404, 
            detail="Subject not found"
        )

    from database import Task
    
    task_result = await session.execute(select(Task).where(Task.subject_id == subject_id))
    task_count = len(task_result.scalars().all())
    return SubjectWithTasksOut.from_orm(subject).copy(update={"task_count": task_count})

@router.put("/{subject_id}", response_model=SubjectOut)
async def update_subject(subject_id: int, subject: SubjectUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Subject).where(Subject.id == subject_id))
    db_subject = result.scalar_one_or_none()
    
    if db_subject is None:
        raise HTTPException(
            status_code=404, 
            detail="Subject not found"
        )
    
    if subject.name is not None:
        result = await session.execute(select(Subject).where(Subject.name == subject.name))
        existing = result.scalar_one_or_none()
        
        if existing and existing.id != subject_id:
            raise HTTPException(
                status_code=400, 
                detail="Subject with this name already exists"
            )
        db_subject.name = subject.name
    await session.commit()
    await session.refresh(db_subject)
    return db_subject

@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(subject_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Subject).where(Subject.id == subject_id))
    subject = result.scalar_one_or_none()
    
    if subject is None:
        raise HTTPException(
            status_code=404, detail="Subject not found"
        )
    await session.delete(subject)
    await session.commit()
    return None
