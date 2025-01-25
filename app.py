from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import os
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

PROFILE_PICTURES_FOLDER = os.path.join('static', 'images', 'profile_pictures')
PROJECT_PICTURES_FOLDER = os.path.join('static', 'images', 'project_pictures')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['PROFILE_PICTURES_FOLDER'] = PROFILE_PICTURES_FOLDER
app.config['PROJECT_PICTURES_FOLDER'] = PROJECT_PICTURES_FOLDER

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
    with db.session() as session:
        return session.get(User, int(user_id))


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
    background_picture = db.Column(db.String(200), nullable=False,default='images/project_pictures/default-bg.jpg')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
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
    user_projects = Project.query.filter_by(created_by=current_user.id).all()

    return render_template('dashboard.html', username=current_user.username, projects=user_projects)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

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
                new_filename = f"{uuid.uuid4().hex}.{file_extension}"
                file_path = os.path.join(app.config['PROFILE_PICTURES_FOLDER'], new_filename)
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

@app.route('/create-project', methods=['POST'])
@login_required
def create_project():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        bg_picture = 'images/project_pictures/default-bg.jpg'

        if not name or not description:
            return jsonify({'success': False, 'message': 'Name and description are required'}), 400
        try:
            new_project = Project(
                name=name,
                description=description,
                background_picture=bg_picture,
                created_by=current_user.id,
                status="In Progress",
            )

            db.session.add(new_project)
            db.session.commit()

            if 'background_picture' in request.files:
                file = request.files['background_picture']
                if file and allowed_file(file.filename):
                    file_extension = file.filename.rsplit('.', 1)[1].lower()
                    new_filename = f"{uuid.uuid4().hex}.{file_extension}"
                    file_path = os.path.join(app.config['PROJECT_PICTURES_FOLDER'], new_filename)
                    file.save(file_path)

                    new_project.background_picture = os.path.join('images', 'project_pictures', new_filename).replace("\\", "/")
                    db.session.commit()

            return jsonify({'success': True, 'message': 'Project created successfully'}), 200
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error creating project: {str(e)}'}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
