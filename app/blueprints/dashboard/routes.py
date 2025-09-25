from flask import render_template
from flask_login import login_required, current_user
from ...models import Project, User
from ...services.progress import estimate_project_progress, calculate_task_progress
from . import bp

@bp.route("/")
@login_required
def root():
    return dashboard()

@bp.route("/dashboard")
@login_required
def dashboard():
    created_projects = Project.query.filter_by(created_by=current_user.id).all()
    user = User.query.get(current_user.id)
    contributed_projects = user.contributed_projects
    all_projects = created_projects + contributed_projects
    for project in all_projects:
        project.progress = estimate_project_progress(project.status)
    active_tasks = user.tasks_contributed
    for task in active_tasks:
        task.progress = calculate_task_progress(task)
        if task.deadline:
            days_left = (task.deadline.date() - calculate_task_progress.__globals__["date"].today()).days
            task.days_left = days_left if days_left >= 0 else 0
        else:
            task.days_left = None
    return render_template("dashboard/dashboard.html", username=current_user.username, projects=all_projects, tasks=active_tasks)