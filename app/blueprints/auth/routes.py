from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user
from ...extensions import db, bcrypt
from ...models import User
from . import bp
from ...config import BaseConfig
from ...utils.files import allowed_file
import os, uuid

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))
    if request.method == "POST":
        email_user = request.form.get("email_user")
        password = request.form.get("password")
        existing_user = (
            User.query.filter_by(email=email_user).first() or User.query.filter_by(username=email_user).first()
        )
        if existing_user and bcrypt.check_password_hash(existing_user.password, password):
            flash("Account login", "success")
            login_user(existing_user)
            return redirect(url_for("dashboard.dashboard"))
        flash("Login failed", "danger")
    return render_template("auth/login.html")

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        fullname = request.form.get("fullname")
        password = bcrypt.generate_password_hash(request.form.get("password")).decode("utf-8")
        confirm_password = request.form.get("confirm_password")

        if confirm_password != request.form.get("password"):
            flash("The passwords do not match.", "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            flash("Email or Username already registered. Please log in.", "danger")
            return redirect(url_for("auth.register"))

        # fallback implicit (relativ la /static)
        profile_picture_rel = "images/profile_pictures/profile.png"

        new_user = User(
            username=username,
            fullname=fullname,
            email=email,
            password=password,
            profile_picture=profile_picture_rel
        )
        db.session.add(new_user)
        db.session.commit()

        # upload (opțional)
        if "profile_picture" in request.files:
            file = request.files["profile_picture"]
            if file and allowed_file(file.filename):  # folosește util-ul tău
                ext = file.filename.rsplit(".", 1)[1].lower()
                new_filename = f"{uuid.uuid4().hex}.{ext}"

                # DIR absolut din config (din create_app)
                folder_abs = current_app.config["UPLOAD_PROFILE_DIR"]
                os.makedirs(folder_abs, exist_ok=True)

                # salvezi pe disc
                file_path_abs = os.path.join(folder_abs, new_filename)
                file.save(file_path_abs)

                # în DB salvezi DOAR relativ la /static
                new_user.profile_picture = os.path.join("images", "profile_pictures", new_filename).replace("\\", "/")
                db.session.commit()

        flash("Account created successfully.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")