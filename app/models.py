from sqlalchemy import String, ForeignKey, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import Optional, List
from datetime import datetime

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owned_projects: Mapped[List["Project"]] = relationship(
        "Project", 
        back_populates="owner", 
        cascade="all, delete-orphan"
    )
    assigned_tasks: Mapped[List["Task"]] = relationship(
        "Task", 
        back_populates="assignee",
        foreign_keys="Task.assignee_id"
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        onupdate=func.now(),
        nullable=True
    )

    owner: Mapped["User"] = relationship("User", back_populates="owned_projects")
    tasks: Mapped[List["Task"]] = relationship(
        "Task", 
        back_populates="project", 
        cascade="all, delete-orphan"
    )

    @property
    def task_count(self) -> int:
        return len(self.tasks)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="todo")
    project_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("projects.id", ondelete="CASCADE"), 
        nullable=False
    )
    assignee_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id"), 
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        onupdate=func.now(),
        nullable=True
    )

    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    assignee: Mapped[Optional["User"]] = relationship(
        "User", 
        back_populates="assigned_tasks",
        foreign_keys=[assignee_id]
    )