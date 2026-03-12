from flask_login import UserMixin
from app.extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from .base import BaseModel
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Role(BaseModel):
    __tablename__ = 'roles'
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    users = db.relationship('User', backref='role', lazy=True)

class User(UserMixin, BaseModel):
    __tablename__ = 'users'
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    active = db.Column(db.Boolean, default=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def is_admin(self):
        return self.role and self.role.name == 'Admin'

class AuditLog(BaseModel):
    __tablename__ = 'audit_logs'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(100), nullable=False)
    entity_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text) # JSON string
    ip_address = db.Column(db.String(45))
