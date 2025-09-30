from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_
from ...extensions import db, bcrypt
from ...models import User, Project
from ...services.progress import estimate_project_progress
from . import bp

@bp.route("/profile")
@bp.route("/profile/<int:user_id>")
@login_required
def profile(user_id=None):
    user = current_user if user_id is None else User.query.get_or_404(user_id)
    if user.id == current_user.id:
        user_projects = Project.query.filter_by(created_by=user.id).all()
    else:
        user_projects = (
            Project.query
            .filter(
                Project.created_by == user.id,
                or_(Project.is_public == True, Project.contributors.any(id=current_user.id))
            ).all()
        )
    for project in user_projects:
        project.progress = estimate_project_progress(project.status)
    return render_template("profile/user-profile.html", username=user.username, fullname=user.fullname, email=user.email, profile_picture=user.profile_picture, projects=user_projects, is_self=(user.id == current_user.id))

@bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    data = request.get_json() or {}
    current_password = data.get("currentPassword")
    new_password = data.get("newPassword")

    if not bcrypt.check_password_hash(current_user.password, current_password):
        return jsonify({"error": "Current password is incorrect"}), 400

    current_user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")
    db.session.commit()

    return jsonify({"success": True, "message": "Password changed successfully"})

@bp.route("/edit-fullname", methods=["POST"])
@login_required
def edit_fullname():
    new_fullname = request.json.get("fullname")
    if not new_fullname:
        return {"error": "Full name is required"}, 400
    current_user.fullname = new_fullname
    db.session.commit()
    return {"message": "Full name updated successfully"}, 200

@bp.route("/edit-email", methods=["POST"])
@login_required
def edit_email():
    new_email = request.json.get("email")
    if not new_email:
        return {"error": "Email is required"}, 400
    if User.query.filter_by(email=new_email).first():
        return {"error": "Email is already in use"}, 400
    current_user.email = new_email
    db.session.commit()
    return {"message": "Email updated successfully"}, 200

@bp.route("/edit-username", methods=["POST"])
@login_required
def edit_username():
    data = request.get_json() or {}
    new_username = (data.get("username") or "").strip()

    if not new_username:
        return {"error": "Username cannot be empty."}, 400

    # unicitate (alt user cu același username)
    exists = User.query.filter(
        User.username == new_username,
        User.id != current_user.id
    ).first()
    if exists:
        return {"error": "Username already taken."}, 409

    current_user.username = new_username
    db.session.commit()
    return {"message": "Username updated successfully."}, 200
