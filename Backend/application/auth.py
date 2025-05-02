from flask import request
from flask_restful import Resource
from flask_security import login_user
from flask_security.utils import verify_password, hash_password
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from .models import User, Role, UserRole
from .database import db
from .utils import validate_phone, validate_password
from flask import current_app as app

class RegisterResource(Resource):
    def post(self):
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['phone_number', 'password', 'name', 'role']
        if not all(key in data for key in required_fields):
            return {'message': 'Missing required fields'}, 400
        
        # Validate phone number format
        if not validate_phone(data['phone_number']):
            return {'message': 'Invalid phone number format'}, 400
        
        # Validate password strength
        if not validate_password(data['password']):
            return {
                'message': 'Password must be at least 8 characters long',
                'password_requirements': {
                    'min_length': 8,
                    'requires_special_char': False,
                    'requires_number': False
                }
            }, 400
        
        # Validate role
        valid_roles = ['installer', 'supervisor', 'admin']
        if data['role'].lower() not in valid_roles:
            return {
                'message': 'Invalid role specified',
                'valid_roles': valid_roles
            }, 400
        
        # Check if phone number already exists
        if User.query.filter_by(phone_number=data['phone_number']).first():
            return {'message': 'Phone number already registered'}, 400
        
        # Supervisor validation for installers
        supervisor = None
        if data['role'].lower() == 'installer':
            if 'supervisor_id' not in data:
                return {'message': 'Supervisor ID is required for installers'}, 400
            
            supervisor = User.query.get(data['supervisor_id'])
            if not supervisor:
                return {
                    'message': f'No user found with supervisor ID {data["supervisor_id"]}',
                    'suggestion': 'Create supervisor first or check ID'
                }, 400
            
            if not any(r.name.lower() == 'supervisor' for r in supervisor.roles):
                return {
                    'message': f'User with ID {data["supervisor_id"]} is not a supervisor',
                    'user_details': {
                        'id': supervisor.id,
                        'name': supervisor.name,
                        'roles': [r.name for r in supervisor.roles]
                    }
                }, 400

        try:
            # Create user using Flask-Security's datastore
            user = app.security.datastore.create_user(
                name=data['name'],
                phone_number=data['phone_number'],
                password=hash_password(data['password']),
                active=True,
                roles=[data['role'].lower()]
            )
            
            # Assign supervisor if installer
            if data['role'].lower() == 'installer':
                user.supervisor_id = supervisor.id
            
            db.session.commit()
            
            return {
                'message': 'User registered successfully',
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'phone_number': user.phone_number,
                    'role': data['role'].lower(),
                    'supervisor_id': user.supervisor_id if data['role'].lower() == 'installer' else None
                }
            }, 201
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Error registering user: {str(e)}')
            return {
                'message': 'Error creating user',
                'error': str(e)
            }, 500

class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        
        if not all(key in data for key in ['phone_number', 'password']):
            return {'message': 'Missing phone or password'}, 400
        
        user = User.query.filter_by(phone_number=data['phone_number']).first()
        
        if not user or not verify_password(data['password'], user.password):
            return {'message': 'Invalid phone or password'}, 401
        
        if not user.active:
            return {'message': 'Account is not active'}, 403
        
        login_user(user)
        access_token = create_access_token(identity=str(user.id))
        # access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return {
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'phone_number': user.phone_number,
                'name': user.name,
                'roles': [role.name for role in user.roles],
                'supervisor_id': user.supervisor_id
            }
        }, 200

class LogoutResource(Resource):
    @jwt_required()
    def post(self):
        return {'message': 'Successfully logged out'}, 200

class TokenRefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user)
        return {'access_token': new_token}, 200