import email
from flask import jsonify, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user
from ...extensions import db, bcrypt
from ...models import User
from . import bp
from ...config import BaseConfig
from ...utils.files import allowed_file
import os, uuid
from app.utils.password_utils import password_complexity

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
        password_raw = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if confirm_password != password_raw:
            flash("The passwords do not match.", "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            flash("Email or Username already registered.", "danger")
            return redirect(url_for("auth.register"))

        checks = password_complexity(password_raw, username, email)
        if not checks["strong"]:
            flash("Password does not meet security requirements.", "danger")
            if not checks["length"]:
                flash("Password must be at least 8 characters long.", "warning")
            if not checks["uppercase"]:
                flash("Password must contain at least one uppercase letter.", "warning")
            if not checks["lowercase"]:
                flash("Password must contain at least one lowercase letter.", "warning")
            if not checks["digit"] and not checks["special"]:
                flash("Password must contain at least one number or special character.", "warning")
            if checks["username_in_password"]:
                flash("Password must not contain your username.", "warning")
            if checks["email_in_password"]:
                flash("Password must not contain part of your email address.", "warning")
            if checks["simple_sequences"]:
                flash("Password must not contain simple patterns like '123', 'abc', or 'qwe'.", "warning")
            return redirect(url_for("auth.register"))

        hashed_password = bcrypt.generate_password_hash(password_raw).decode("utf-8")

        new_user = User(
            username=username,
            fullname=fullname,
            email=email,
            password=hashed_password,
            profile_picture="images/profile_pictures/profile.png"
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")

@bp.route("/password-check", methods=["POST"])
def password_check():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "") or ""
    email = data.get("email", "") or ""
    password = data.get("password", "") or ""
    result = password_complexity(password, username, email)
    return jsonify(result)