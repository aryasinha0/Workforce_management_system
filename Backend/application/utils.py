import re
from werkzeug.utils import secure_filename
from flask import current_app

def validate_phone(phone):
    """Validate phone number format"""
    return re.match(r'^\+?[0-9]{8,15}$', phone) is not None

def validate_password(password):
    """Validate password meets requirements"""
    return len(password) >= 8  # You can add more complex validation if needed

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']