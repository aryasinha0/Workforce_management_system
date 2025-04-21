from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    active = db.Column(db.Boolean, nullable = False, default = False)
    fs_uniquifier = db.Column(db.String, unique = True, nullable = False)
    roles = db.relationship('Role', backref = 'bearer', secondary = 'user_role')
    
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique = True)
    description = db.Column(db.String)

class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)  # date and time of attendance

    user_image = db.Column(db.String(255), nullable=True)  # path or URL to user image
    time = db.Column(db.Time, nullable=False)              # separate time field if needed
    location = db.Column(db.String(255), nullable=True)    # address or location info

class Tracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float, nullable=True)  # optional: GPS accuracy in meters
  


class FaultyMeter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    serial_no = db.Column(db.String(255), nullable=False)
    meter_image = db.Column(db.String(255), nullable=False)
    remark = db.Column(db.String, nullable=False)
