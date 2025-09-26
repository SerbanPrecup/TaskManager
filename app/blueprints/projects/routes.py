from flask import render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from ...extensions import db
from ...models import Project, User
from ...config import BaseConfig
from ...utils.files import allowed_file
import os, uuid
from . import bp

@bp.route("/projects")
@login_required
def list_projects():
    created = Project.query.filter_by(created_by=current_user.id).all()
    user = db.session.get(User, current_user.id)
    contributed = user.contributed_projects
    all_projects = created + contributed

    # dacă nu ai deja calculul progresului
    for p in all_projects:
        try:
            p.progress = estimate_project_progress(p.status)
        except Exception:
            p.progress = 0

    return render_template("projects/projects.html", projects=all_projects)

@bp.route("/project/<int:project_id>")
@login_required
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template("projects/project.html", project=project)

@bp.route("/create-project", methods=["GET", "POST"])
@login_required
def create_project():
    if request.method == "GET":
        return render_template("projects/create-project.html", all_users=User.query.all())

    # POST (multipart/form-data din FormData)
    name = request.form.get("name")
    description = request.form.get("description")
    is_public = request.form.get("is_public") == "true"
    contributor_ids = request.form.getlist("contributors")

    if not name or not description:
        return jsonify({"success": False, "message": "Name and description are required"}), 400

    # valoare implicită relativă la /static pentru DB
    bg_picture_rel = "images/project_pictures/default-bg.jpg"

    # dacă se încarcă o imagine
    if "background_picture" in request.files:
        file = request.files["background_picture"]
        if file and allowed_file(file.filename):  # allowed_file să citească ALLOWED_EXTENSIONS din config
            ext = file.filename.rsplit(".", 1)[1].lower()
            new_filename = f"{uuid.uuid4().hex}.{ext}"

            # director ABSOLUT din config (setat în create_app)
            folder_abs = current_app.config["UPLOAD_PROJECT_DIR"]
            os.makedirs(folder_abs, exist_ok=True)

            # salvează pe disc
            abs_path = os.path.join(folder_abs, new_filename)
            file.save(abs_path)

            # în DB păstrezi DOAR calea relativă la /static
            bg_picture_rel = os.path.join("images", "project_pictures", new_filename).replace("\\", "/")

    # creează proiect
    new_project = Project(
        name=name,
        description=description,
        background_picture=bg_picture_rel,
        created_by=current_user.id,
        status="In Progress",
        is_public=is_public
    )

    # adaugă contribuitori
    for uid in contributor_ids:
        user = User.query.get(int(uid))
        if user:
            new_project.contributors.append(user)

    db.session.add(new_project)
    db.session.commit()
    return jsonify({"success": True, "message": "Project created successfully"})

@bp.route("/project/<int:project_id>/add-contributor", methods=["POST"])
@login_required
def add_contributor(project_id):
    data = request.get_json()
    username = data.get("username", "").strip()
    if not username:
        return jsonify({"success": False, "message": "Username is required"}), 400
    project = Project.query.get_or_404(project_id)
    if current_user.id != project.created_by:
        return jsonify({"success": False, "message": "You do not have permission to add contributors"}), 403
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"success": False, "message": f"User \"{username}\" not found"}), 404
    if user in project.contributors:
        return jsonify({"success": False, "message": f"User \"{username}\" is already a contributor"}), 409
    project.contributors.append(user)
    db.session.commit()
    return jsonify({"success": True, "message": f"User \"{username}\" added successfully!"}), 200

@bp.route("/project/<int:project_id>/update-status", methods=["POST"])
@login_required
def update_project_status(project_id):
    project = Project.query.get_or_404(project_id)
    if project.created_by != current_user.id:
        return jsonify({"success": False, "message": "Only the creator can update project status."}), 403
    data = request.get_json()
    new_status = data.get("status")
    allowed = ["Not Started","In Progress","On Hold","Needs Review","Completed","Cancelled","Delayed"]
    if new_status not in allowed:
        return jsonify({"success": False, "message": "Invalid status selected."}), 400
    project.status = new_status
    db.session.commit()
    return jsonify({"success": True, "message": f"Status updated to \"{new_status}\""}), 200

@bp.route("/project/<int:project_id>/toggle-public", methods=["POST"])
@login_required
def toggle_project_visibility(project_id):
    project = Project.query.get_or_404(project_id)
    if project.created_by != current_user.id:
        return jsonify({"success": False, "message": "You can only update your own project visibility."}), 403
    make_public = request.get_json().get("is_public", False)
    project.is_public = make_public
    db.session.commit()
    return jsonify({"success": True, "message": "Visibility updated."})