from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user, LoginManager,login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
db  = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String(20),nullable=False, unique=True)
    password = db.Column(db.String(80),nullable=False)
    email = db.Column(db.String(100),nullable=False, unique=True)

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
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100),nullable=False)
    description = db.Column(db.String(1000),nullable=False)
    id_project = db.Column(db.Integer,db.ForeignKey('projects.id'),nullable=False)
    contributors = db.Column(db.String(1000),nullable=True)
    status = db.Column(db.String(100),nullable=False)
    priority = db.Column(db.Integer,nullable=False)
    deadline = db.Column(db.DateTime,default=datetime.utcnow)
    completed_at = db.Column(db.DateTime,default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_user = request.form.get('email_user')
        password = request.form.get('password')

        existing_user = User.query.filter_by(email=email_user).first() or User.query.filter_by(username=email_user).first()

        if existing_user and bcrypt.check_password_hash(existing_user.password, password):
            flash('Account login','success')
            return render_template('dashboard.html')

        flash('Login failed','danger')




    return render_template('login.html')

@app.route('/dashboard',methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)

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
        password = bcrypt.generate_password_hash(request.form.get('password'))

        existing_email = User.query.filter_by(email=email).first()
        existing_username = User.query.filter_by(username=username).first()
        if existing_email or existing_username:
            flash('Email or Username already registered. Please log in.', 'danger')
            return redirect(url_for('register'))

        if bcrypt.check_password_hash(password, request.form.get('confirm_password')):
            new_user = User(username=username, email=email, password=password);
            db.session.add(new_user)
            db.session.commit()
            flash('Acount created.', 'success')
            return redirect(url_for('login'))

        flash("The password does not match.", 'danger')


    return render_template('register.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

