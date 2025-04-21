from flask import Flask
from application.models import *
from application.config import *
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security import hash_password
app = None

def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app,datastore)
    app.app_context().push()
    return app
app = create_app()

# I want to create default user and role entries into the database
with app.app_context():
    db.create_all()
    app.security.datastore.find_or_create_role(name='admin', description='Admin')
    app.security.datastore.find_or_create_role(name='installer', description='Installer')
    app.security.datastore.find_or_create_role(name='supervisor', description='Supervisor')
    db.session.commit()
    if not app.security.datastore.find_user(name = "admin"):
        app.security.datastore.create_user(name = "admin", phone_number = "1234567890", password = hash_password("admin"),roles = ["admin"])
        db.session.commit()

from application.routes import *



if __name__ == "__main__":
    app.run()