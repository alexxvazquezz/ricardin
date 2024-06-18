from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone_number = db.Column(db.String(16))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', backref='users')

    def __init__(self, email, password, first_name=None, last_name=None, phone_number=None, role=None):
        self.email = email
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.role = role

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {'id': self.id, 'email': self.email, 'first_name': self.first_name, 'last_name': self.last_name, 'phone_number': self.phone_number, 'role': self.role.name if self.role else None}
    
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    social_security = db.Column(db.String(128), nullable=False, unique=True)
    employee_type = db.Column(db.String(64), default='full-time')  # Default value
    hourly_wage = db.Column(db.Float, default=0.0)  # Default value

    user = db.relationship('User', backref='employee')

    def __init__(self, user, social_security, employee_type='full-time', hourly_wage=0.0):
        self.user = user
        self.social_security = social_security
        self.employee_type = employee_type
        self.hourly_wage = hourly_wage

    def to_dict(self):
        return {
            'id': self.id, 
            'user': {
                'id': self.user.id,
                'email': self.user.email,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name
            },
            'social_security': self.social_security, 
            'employee_type': self.employee_type, 
            'hourly_wage': self.hourly_wage
        }
    