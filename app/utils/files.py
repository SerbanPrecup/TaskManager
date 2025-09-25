import os
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename: str, allowed_extensions=None) -> bool:
    if allowed_extensions is None:
        from flask import current_app
        allowed_extensions = current_app.config["ALLOWED_EXTENSIONS"]
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

def ensure_dirs(*paths: str) -> None:
    for p in paths:
        os.makedirs(p, exist_ok=True)