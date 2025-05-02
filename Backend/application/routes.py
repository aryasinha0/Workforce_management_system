from flask import current_app as app, jsonify, request
from flask_security import auth_required, roles_required, current_user
from flask_security import hash_password
from .database import db
from .models import User, Role

@app.route("/", methods = ['GET','POST'])
def home():
    return "<h1>This is a home page</h1>"


@app.route("/api/admin")
@auth_required("token")       # Authentication
@roles_required("admin")      # RBAC/Authorization
def admin_home():
    return jsonify({
        "message":"Admin logged in successfully"
    })


@app.route("/api/installer")
@auth_required("token")
@roles_required("installer")
def installer_home():
    user = current_user()
    return jsonify({
        "username": user.name,
        "email": user.email,
        "password":user.password
    })

@app.route("/api/supervisor")
@auth_required("token")
@roles_required("supervisor")
def supervisor_home():
    user = current_user()
    return jsonify({
        "username": user.name,
        "email": user.email,
        "password":user.password
    })

@app.post("/api/register")
def create_user():
    credentials = request.get_json()
    if not app.security.datastore.find_user(email = credentials["email"]):
        app.security.datastore.create_user(username = credentials["username"],
                                           email = credentials["email"],
                                           password = hash_password(credentials['password']),
                                           roles = ['user'])
        db.session.commit()
        return jsonify({
            "message":"user created successfully"
        }),201
    return jsonify({
        "message":"user already exists"
    }),400
    