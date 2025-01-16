from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join('static', 'images', 'profile_pictures')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(os.path.join('static', 'images', 'profile_pictures'), exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=True, unique=True)
    profile_picture = db.Column(db.String(200), nullable=False,default='images/profile_pictures/profile.png')

    projects_created = db.relationship('Project', backref='creator', lazy=True)


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Corectat
    contributors = db.Column(db.String(1000), nullable=True)
    tasks = db.relationship('Task', backref='project', lazy=True)
    status = db.Column(db.String(100), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    id_project = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    contributors = db.Column(db.String(1000), nullable=True)
    status = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    deadline = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email_user = request.form.get('email_user')
        password = request.form.get('password')

        existing_user = User.query.filter_by(email=email_user).first() or User.query.filter_by(
            username=email_user).first()

        if existing_user and bcrypt.check_password_hash(existing_user.password, password):
            flash('Account login', 'success')
            login_user(existing_user)
            return render_template('dashboard.html')

        flash('Login failed', 'danger')

    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         email = request.form.get('email')
#         password = bcrypt.generate_password_hash(request.form.get('password'))
#         confirm_password = request.form.get('confirm_password')
#
#         if 'profile_picture' in request.files:
#             file = request.files['profile_picture']
#             if file and allowed_file(file.filename):
#                 filename = secure_filename(file.filename)
#                 profile_picture = None
#             else:
#                 profile_picture = None
#         else:
#             profile_picture = 'images/profile_pictures/profile.png'
#
#         existing_email = User.query.filter_by(email=email).first()
#         existing_username = User.query.filter_by(username=username).first()
#         if existing_email or existing_username:
#             flash('Email or Username already registered. Please log in.', 'danger')
#             return redirect(url_for('register'))
#         if confirm_password != request.form.get('password'):
#             flash("The password does not match.", 'danger')
#             return redirect(url_for('register'))
#
#         new_user = User(
#             username=username,
#             email=email,
#             password=password,
#             profile_picture=profile_picture
#         )
#
#         db.session.add(new_user)
#         db.session.commit()
#
#         if file and allowed_file(file.filename):
#
#             filename = f"profile-picture{new_user.id}.{file.filename.rsplit('.', 1)[1].lower()}"
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#
#             new_user.profile_picture = os.path.join('images', 'profile_pictures', filename).replace("\\", "/")
#
#             db.session.commit()
#
#         flash('Account created.', 'success')
#         return redirect(url_for('login'))
#
#     return render_template('register.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         email = request.form.get('email')
#         password = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
#         confirm_password = request.form.get('confirm_password')
#
#         # Verificare confirmare parolă
#         if confirm_password != request.form.get('password'):
#             flash("The passwords do not match.", 'danger')
#             return redirect(url_for('register'))
#
#         # Verificare dacă email-ul sau username-ul există deja
#         existing_email = User.query.filter_by(email=email).first()
#         existing_username = User.query.filter_by(username=username).first()
#         if existing_email or existing_username:
#             flash('Email or Username already registered. Please log in.', 'danger')
#             return redirect(url_for('register'))
#
#         # Setare imagine implicită
#         profile_picture = 'images/profile_pictures/profile.png'
#
#         # Gestionare fișier imagine dacă este trimis
#         if 'profile_picture' in request.files:
#             file = request.files['profile_picture']
#             if file and allowed_file(file.filename):
#                 filename = secure_filename(file.filename)
#                 file_extension = filename.rsplit('.', 1)[1].lower()
#                 new_filename = f"profile-picture-{username}.{file_extension}"
#                 file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
#                 profile_picture = f"images/profile_pictures/{new_filename}"
#
#         # Creare utilizator nou
#         new_user = User(
#             username=username,
#             email=email,
#             password=password,
#             profile_picture=profile_picture
#         )
#         db.session.add(new_user)
#         db.session.commit()
#
#         flash('Account created successfully.', 'success')
#         return redirect(url_for('login'))
#
#     return render_template('register.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
        confirm_password = request.form.get('confirm_password')

        if confirm_password != request.form.get('password'):
            flash("The passwords do not match.", 'danger')
            return redirect(url_for('register'))

        existing_email = User.query.filter_by(email=email).first()
        existing_username = User.query.filter_by(username=username).first()
        if existing_email or existing_username:
            flash('Email or Username already registered. Please log in.', 'danger')
            return redirect(url_for('register'))

        profile_picture = 'images/profile_pictures/profile.png'

        new_user = User(
            username=username,
            email=email,
            password=password,
            profile_picture=profile_picture
        )
        db.session.add(new_user)
        db.session.commit()

        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                file_extension = file.filename.rsplit('.', 1)[1].lower()
                new_filename = f"profile-picture{new_user.id}.{file_extension}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                file.save(file_path)

                new_user.profile_picture = os.path.join('images', 'profile_pictures', new_filename).replace("\\", "/")
                db.session.commit()

        flash('Account created successfully.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    return render_template('projects.html')


@app.route('/history', methods=['GET', 'POST'])
@login_required
def history():
    return render_template('history.html')


@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    return render_template('active-tasks.html')


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template(
        'user-profile.html',
        username=current_user.username,
        email=current_user.email,
        profile_picture=current_user.profile_picture
    )
@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.json
    new_password = data.get('newPassword')

    if not new_password:
        return {"error": "Password is required"}, 400

    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    current_user.password = hashed_password
    db.session.commit()

    return {"message": "Password changed successfully"}, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
