from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_session, Course, Subject
from models import CourseCreate, CourseUpdate, CourseOut, CourseWithTasksOut
from typing import List

router = APIRouter(
    prefix="/courses",
    tags=["courses"],
)

@router.post("/", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
async def create_course(course: CourseCreate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Subject).where(Subject.id == course.subject_id))
    subject = result.scalar_one_or_none()
    
    if subject is None:
        raise HTTPException(
            status_code=404, 
            detail="Subject not found"
        )
    result = await session.execute(select(Course).where(Course.name == course.name, Course.subject_id == course.subject_id))
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="Course with this name already exists in this subject"
        )
    db_course = Course(name=course.name, subject_id=course.subject_id)
    session.add(db_course)
    await session.commit()
    await session.refresh(db_course)
    return db_course

@router.get("/", response_model=List[CourseOut])
async def read_courses(skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Course).offset(skip).limit(limit))
    courses = result.scalars().all()
    return courses

@router.get("/{course_id}", response_model=CourseWithTasksOut)
async def read_course(course_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    
    if course is None:
        raise HTTPException(
            status_code=404, 
            detail="Course not found"
        )
    
    from database import Task

    task_result = await session.execute(select(Task).where(Task.course_id == course_id))
    task_count = len(task_result.scalars().all())
    return CourseWithTasksOut.from_orm(course).copy(update={"task_count": task_count})

@router.put("/{course_id}", response_model=CourseOut)
async def update_course(course_id: int, course: CourseUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Course).where(Course.id == course_id))
    db_course = result.scalar_one_or_none()
    
    if db_course is None:
        raise HTTPException(
            status_code=404, 
            detail="Course not found"
        )
    
    if course.name is not None:
        result = await session.execute(select(Course).where(Course.name == course.name, Course.subject_id == db_course.subject_id))
        existing = result.scalar_one_or_none()
        
        if existing and existing.id != course_id:
            raise HTTPException(
                status_code=400, 
                detail="Course with this name already exists in this subject"
            )
        db_course.name = course.name
    
    if course.subject_id is not None:
        result = await session.execute(select(Subject).where(Subject.id == course.subject_id))
        subject = result.scalar_one_or_none()
        
        if subject is None:
            raise HTTPException(
                status_code=404, 
                detail="Subject not found"
            )
        db_course.subject_id = course.subject_id
    await session.commit()
    await session.refresh(db_course)
    return db_course

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(course_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    
    if course is None:
        raise HTTPException(
            status_code=404, 
            detail="Course not found"
        )
    await session.delete(course)
    await session.commit()
    return None

@router.get("/{course_id}/users", response_model=List[dict])
async def get_users_by_course(course_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    
    if course is None:
        raise HTTPException(
            status_code=404, 
            detail="Course not found"
        )
    
    from database import user_courses, User
    
    result = await session.execute(
        select(User).select_from(user_courses.join(User, user_courses.c.user_id == User.id))
        .where(user_courses.c.course_id == course_id)
    )
    users = result.scalars().all()
    return [{"id": u.id, "email": u.email} for u in users]
