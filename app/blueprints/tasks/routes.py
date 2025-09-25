from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from ...extensions import db
from ...models import Task, Project, User
from . import bp
from datetime import datetime

@bp.route("/tasks")
@login_required
def tasks_page():
    return render_template("tasks/active-tasks.html")

@bp.route("/project/<int:project_id>/add-task", methods=["POST"])
@login_required
def add_task(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user not in project.contributors and current_user.id != project.created_by:
        return jsonify({"success": False, "message": "You must be a contributor to add tasks."}), 403
    data = request.get_json()
    name = data.get("name")
    description = data.get("description")
    status = data.get("status")
    priority = data.get("priority")
    deadline_str = data.get("deadline")
    contributor_ids = data.get("contributors", [])
    if not name or not description or not status or not priority:
        return jsonify({"success": False, "message": "Missing required fields."}), 400
    try:
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d") if deadline_str else None
        new_task = Task(name=name, description=description, status=status, priority=int(priority), deadline=deadline, id_project=project.id)
        db.session.add(new_task)
        db.session.flush()
        for uid in contributor_ids:
            user = User.query.get(int(uid))
            if user:
                new_task.contributors.append(user)
        project.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({"success": True, "message": "Task created successfully."}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@bp.route("/task/<int:task_id>/update-status", methods=["POST"])
@login_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    new_status = request.get_json().get("status")
    if not new_status:
        return jsonify({"success": False, "message": "No status provided"}), 400
    task.status = new_status
    task.project.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"success": True, "message": "Status updated"})