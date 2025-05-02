from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from .models import User, Attendance, Tracking, FaultyMeter, AdverseCondition
from .database import db
from .utils import allowed_file

# For installer attendance
class AttendanceResource(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        
        # Eager load roles to avoid missing relationships
        user = User.query.options(db.joinedload(User.roles)).get(current_user_id)
        
        if not user:
            return {'message': 'User not found'}, 404
        
        # Case-insensitive role check
        if not any(r.name.lower() == 'installer' for r in user.roles):
            return {
                'message': 'Only installers can submit attendance',
                'your_roles': [r.name for r in user.roles]  # Debug info
            }, 403
        
        # Get JSON data instead of form-data
        data = request.get_json()
        
        if not data:
            return {'message': 'No data provided'}, 400
            
        # Validate required fields
        required_fields = ['latitude', 'longitude', 'location', 'selfie']
        if not all(field in data for field in required_fields):
            return {'message': f'Missing required fields. Required: {", ".join(required_fields)}'}, 400
        
        # Validate selfie is a string (URL/path)
        if not isinstance(data['selfie'], str):
            return {'message': 'Selfie must be a URL string'}, 400
        
        # Create attendance record
        now = datetime.now()
        attendance = Attendance(
            user_id=current_user_id,
            date=now.date(),
            time=now.time(),
            user_image=data['selfie'],  # Store the URL/path directly
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            location=data['location']
        )
        
        db.session.add(attendance)
        db.session.commit()
        
        return {
            'message': 'Attendance recorded successfully',
            'data': {
                'attendance_id': attendance.id,
                'selfie_url': data['selfie']
            }
        }, 201
# For installer tracking
from flask_jwt_extended import jwt_required, get_jwt_identity

from datetime import datetime

class TrackingResource(Resource):
    @jwt_required()
    def post(self):
        try:
            current_user = get_jwt_identity()
            data = request.get_json()
            
            # Validate required fields
            if not all(key in data for key in ['latitude', 'longitude', 'location']):
                return {'message': 'Missing required fields: latitude, longitude, location'}, 400
            
            # Create tracking record with auto-generated timestamp
            tracking = Tracking(
                user_id=current_user,
                timestamp=datetime.utcnow(),  # Auto-set timestamp 👈
                latitude=float(data['latitude']),
                longitude=float(data['longitude']),
                location=str(data['location']),
                accuracy=float(data.get('accuracy', 0.0))  # Optional, defaults to 0.0
            )
            
            db.session.add(tracking)
            db.session.commit()
            
            return {'message': 'Location tracked successfully'}, 201
            
        except ValueError as e:
            return {'message': f'Invalid data format: {str(e)}'}, 400
        except Exception as e:
            db.session.rollback()
            return {'message': f'Server error: {str(e)}'}, 500      
class FaultyMeterResource(Resource):
    @jwt_required()
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            
            # Eager load roles to prevent missing relationships
            user = User.query.options(db.joinedload(User.roles)).get(current_user_id)
            if not user:
                return {'message': 'User not found'}, 404
            
            # Case-insensitive role check
            if not any(r.name.lower() == 'installer' for r in user.roles):
                return {
                    'message': 'Only installers can submit faulty meter reports',
                    'your_roles': [r.name for r in user.roles]  # Debug info
                }, 403
            
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['serial_no', 'meter_image', 'remark']
            if not all(field in data for field in required_fields):
                return {'message': f'Missing required fields: {", ".join(required_fields)}'}, 400
            
            # Validate image URL format
            if not data['meter_image'].startswith(('http://', 'https://')):
                return {'message': 'Invalid image URL format'}, 400
            
            # Create record
            faulty_meter = FaultyMeter(
                user_id=current_user_id,
                serial_no=data['serial_no'],
                meter_image=data['meter_image'],
                remark=data['remark'],
                # status/created_at auto-populated
            )
            
            db.session.add(faulty_meter)
            db.session.commit()
            
            return {
                'message': 'Faulty meter report submitted successfully',
                'data': {
                    'report_id': faulty_meter.id,
                    'status': faulty_meter.status
                }
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500
class AdverseConditionResource(Resource):
    @jwt_required()
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            
            # Eager load roles to prevent N+1 query issues
            user = User.query.options(db.joinedload(User.roles)).get(current_user_id)
            
            if not user:
                return {'message': 'User not found'}, 404
                
            # Case-insensitive role check with debug info
            if not any(r.name.lower() == 'installer' for r in user.roles):
                return {
                    'message': 'Only installers can submit adverse conditions',
                    'your_roles': [r.name for r in user.roles]
                }, 403
            
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['condition', 'consumer_id']
            if not all(field in data for field in required_fields):
                return {
                    'message': 'Missing required fields',
                    'required': required_fields,
                    'received': list(data.keys())
                }, 400
            
            # Validate field lengths
            if len(data['consumer_id']) > 50:
                return {'message': 'Consumer ID must be 50 characters or less'}, 400
            
            # Create record
            adverse_condition = AdverseCondition(
                user_id=current_user_id,
                condition=data['condition'],
                consumer_id=data['consumer_id']
                # created_at auto-populated
            )
            
            db.session.add(adverse_condition)
            db.session.commit()
            
            return {
                'message': 'Adverse condition reported successfully',
                'data': {
                    'id': adverse_condition.id,
                    'created_at': adverse_condition.created_at.isoformat()
                }
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'message': f'Server error: {str(e)}'}, 500