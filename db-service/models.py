from extensions import db
from sqlalchemy import Enum
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Role field using Enum to restrict values to 'user', 'mod', or 'admin'
    role = db.Column(Enum('user', 'mod', 'admin', name='role'), nullable=False, default='user')

    def __init__(self, username, email, password, role):
        self.username = username
        self.email = email
        self.password_hash = password
        self.role = role

    def check_password(self, password):
        """Check if the password matches the hash"""
        return check_password_hash(self.password_hash, password)

    def set_password(self, password):
        """Set the password hash in the gateway to protect data while it transits"""
        self.password_hash = password

class Board(db.Model):
    __tablename__ = 'boards'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(256))

    # One-to-many relationship: A board has many threads
    threads = db.relationship('Thread', backref='board', lazy=True, cascade="all, delete-orphan")  # Cascade delete

class Thread(db.Model):
    __tablename__ = 'threads'
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)  # Description field

    # One-to-many relationship: A thread has many posts
    posts = db.relationship('Post', backref='thread', lazy=True, cascade="all, delete-orphan")  # Cascade delete

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('threads.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
