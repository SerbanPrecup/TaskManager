from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import or_
from .extensions import db

project_contributors = db.Table(
    "project_contributors",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    db.Column("project_id", db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
)

task_contributors = db.Table(
    "task_contributors",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    db.Column("task_id", db.Integer, db.ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
)

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    fullname = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=True, unique=True)
    profile_picture = db.Column(db.String(200), nullable=False, default="images/profile_pictures/profile.png")

    projects_created = db.relationship("Project", backref="creator", lazy=True)
    contributed_projects = db.relationship("Project", secondary=project_contributors, back_populates="contributors")
    tasks_contributed = db.relationship("Task", secondary=task_contributors, back_populates="contributors")

    def __repr__(self):
        return f"<User {self.username}>"

class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    background_picture = db.Column(db.String(200), nullable=False, default="images/project_pictures/default-bg.jpg")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(100), nullable=False)
    is_public = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    tasks = db.relationship(
        "Task",
        backref=db.backref("project", lazy=True),
        cascade="all, delete, delete-orphan",
        passive_deletes=True,
        lazy=True,
    )

    contributors = db.relationship("User", secondary=project_contributors, back_populates="contributed_projects")

    def __repr__(self):
        return f"<Project {self.name}>"

class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)

    id_project = db.Column(
        db.Integer,
        db.ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )

    status = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    deadline = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    contributors = db.relationship("User", secondary=task_contributors, back_populates="tasks_contributed")

    def __repr__(self):
        return f"<Task {self.name}>"
