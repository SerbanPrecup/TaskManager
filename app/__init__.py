import os
import sqlite3
from flask import Flask
from .config import DevConfig
from .extensions import db, login_manager, bcrypt, csrf
from sqlalchemy import event
from sqlalchemy.engine import Engine

# 👉 Enable FK constraints for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

def create_app(config_class: type = DevConfig) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Căi ABSOLUTE pentru upload, sub app/static
    app.config["UPLOAD_PROFILE_DIR"] = os.path.join(app.static_folder, "images", "profile_pictures")
    app.config["UPLOAD_PROJECT_DIR"] = os.path.join(app.static_folder, "images", "project_pictures")

    # Creează directoarele dacă lipsesc
    from .utils.files import ensure_dirs
    ensure_dirs(app.config["UPLOAD_PROFILE_DIR"], app.config["UPLOAD_PROJECT_DIR"])

    # Init extensions
    db.init_app(app)   # <-- acum se aplică și PRAGMA-ul de FK
    bcrypt.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from .models import User  # noqa: F401

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Blueprints
    from .blueprints.auth import bp as auth_bp
    from .blueprints.dashboard import bp as dashboard_bp
    from .blueprints.projects import bp as projects_bp
    from .blueprints.tasks import bp as tasks_bp
    from .blueprints.profile import bp as profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(profile_bp)

    # CLI: init-db
    @app.cli.command("init-db")
    def init_db_cmd():
        with app.app_context():
            db.create_all()
            print("Database initialized.")

    return app
