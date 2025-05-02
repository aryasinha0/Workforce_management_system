from datetime import datetime
from .database import db
from flask_security import UserMixin, RoleMixin
import uuid

# Basic details of the user
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)  # Increased length for hashed passwords
    active = db.Column(db.Boolean(), default=True)  # Changed to Boolean()
    fs_uniquifier = db.Column(db.String(255), default=lambda: str(uuid.uuid4()))  # Added default
    roles = db.relationship('Role', backref='bearer', secondary='user_role')
    supervisor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    installers = db.relationship('User', backref=db.backref('supervisor', remote_side=[id]))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.fs_uniquifier is None:
            self.fs_uniquifier = str(uuid.uuid4())
# Roles available
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)  # Admin, Installer, Supervisor
    description = db.Column(db.String)


# User role
class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

# Attendance of the user
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)  # date and time of attendance
    user_image = db.Column(db.String(255), nullable=True)  # path or URL to user image
    time = db.Column(db.Time, nullable=False)              # separate time field if needed
    location = db.Column(db.String(255), nullable=False)    # address or location info
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    user = db.relationship('User', backref='attendances')

# Whole day tracking of the user
class Tracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float)  # optional: GPS accuracy in meters
    
    user = db.relationship('User', backref='trackings')

# Faulty meter data 
class FaultyMeter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    serial_no = db.Column(db.String(255), nullable=False)
    meter_image = db.Column(db.String(255), nullable=False)
    remark = db.Column(db.String, nullable=False)
    status = db.Column(db.String(50), default='Pending')  # Pending, Received, Not Received, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='faulty_meters')

# Adverse field condition
class AdverseCondition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    condition = db.Column(db.Text, nullable=False)
    consumer_id = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='adverse_conditions')