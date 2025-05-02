from flask import Flask
from flask_jwt_extended import JWTManager  # <-- Add this import
from application.models import *
from application.config import *
from application.resources import api, init_api
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security import hash_password

app = None

def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)
    
    # Initialize database
    db.init_app(app)
    
    # Initialize JWT Manager  # <-- Add this block
    jwt = JWTManager(app)
    
    # Initialize API
    init_api(app)
    
    # Setup Flask-Security
    datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, datastore)
    
    app.app_context().push()
    return app

app = create_app()

# Create default user and role entries
with app.app_context():
    db.create_all()
    app.security.datastore.find_or_create_role(name='admin', description='Admin')
    app.security.datastore.find_or_create_role(name='installer', description='Installer')
    app.security.datastore.find_or_create_role(name='supervisor', description='Supervisor')
    db.session.commit()
    
    # Create admin if not exists
    if not app.security.datastore.find_user(name="admin"):
        app.security.datastore.create_user(
            name="admin",
            phone_number="1234567890",
            password=hash_password("admin"),
            roles=["admin"]
        )
    
    # Create a supervisor if none exists
    if not app.security.datastore.find_user(name="supervisor1"):
        app.security.datastore.create_user(
            name="supervisor1",
            phone_number="1234567891",
            password=hash_password("supervisor123"),
            roles=["supervisor"]
        )
    
    db.session.commit()

if __name__ == "__main__":
    app.run()