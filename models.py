from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TaskCreate(BaseModel):
    title: str
    description: str = ""
    subject_id: int
    course_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    subject_id: Optional[int] = None
    course_id: Optional[int] = None

class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    subject_id: int
    course_id: int
    status: str

    model_config = {"from_attributes": True}

class SubjectCreate(BaseModel):
    name: str

class SubjectUpdate(BaseModel):
    name: Optional[str] = None

class SubjectOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}

class CourseCreate(BaseModel):
    name: str
    subject_id: int

class CourseUpdate(BaseModel):
    name: Optional[str] = None
    subject_id: Optional[int] = None

class CourseOut(BaseModel):
    id: int
    name: str
    subject_id: int

    model_config = {"from_attributes": True}

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None

class UserOut(UserBase):
    id: int
    is_active: bool

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class SubjectWithTasksOut(SubjectOut):
    task_count: int = 0

class CourseWithTasksOut(CourseOut):
    task_count: int = 0

class UserWithSubjectsOut(UserOut):
    subjects: List[SubjectOut] = []
    courses: List[CourseOut] = []

class UserWithCoursesOut(UserOut):
    courses: List[CourseOut] = []
