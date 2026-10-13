from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Table, Column
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

echo_sql = os.getenv("SQL_ECHO", "true").lower() == "true"
engine = create_async_engine(DATABASE_URL, echo=echo_sql)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

user_subjects = Table(
    'user_subjects',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('subject_id', Integer, ForeignKey('subjects.id'), primary_key=True)
)

user_courses = Table(
    'user_courses',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    subjects: Mapped[list["Subject"]] = relationship(
        secondary=user_subjects, back_populates="users"
    )
    courses: Mapped[list["Course"]] = relationship(
        secondary=user_courses, back_populates="users"
    )
    tasks: Mapped[list["Task"]] = relationship(back_populates="owner")

class Subject(Base):
    __tablename__ = "subjects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    courses: Mapped[list["Course"]] = relationship(back_populates="subject")
    users: Mapped[list["User"]] = relationship(
        secondary=user_subjects, back_populates="subjects"
    )
    tasks: Mapped[list["Task"]] = relationship(back_populates="subject")

class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    subject: Mapped[Subject] = relationship(back_populates="courses")
    users: Mapped[list["User"]] = relationship(
        secondary=user_courses, back_populates="courses"
    )
    tasks: Mapped[list["Task"]] = relationship(back_populates="course")

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str] = mapped_column(String(1000), default="")
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    status: Mapped[str] = mapped_column(String(20), default="todo")
    owner: Mapped[User] = relationship(back_populates="tasks")
    subject: Mapped[Subject] = relationship(back_populates="tasks")
    course: Mapped[Course] = relationship(back_populates="tasks")

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
