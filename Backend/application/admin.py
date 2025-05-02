from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User, Attendance, FaultyMeter, AdverseCondition, Tracking, Role
from .database import db
from flask import request

class AdminUsersResource(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user = User.query.options(db.joinedload(User.roles)).get(current_user_id)
            
        if not user:
            return {'message': 'User not found'}, 404

        # Case-insensitive role check for supervisor
        if not any(r.name.lower() == 'admin' for r in user.roles):
            return {
                'message': 'Only admins can access this resource',
                'your_roles': [r.name for r in user.roles]
            }, 403
        
        users = User.query.all()
        
        return {
            'users': [
                {
                    'id': u.id,
                    'phone_number': u.phone_number,
                    'name': u.name,
                    'roles': [r.name for r in u.roles],
                    'supervisor_id': u.supervisor_id,
                    'active': u.active,
                    'created_at': u.created_at.isoformat()
                } for u in users
            ]
        }, 200

class AdminAttendanceResource(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user = User.query.options(db.joinedload(User.roles)).get(current_user_id)
            
        if not user:
            return {'message': 'User not found'}, 404

        # Case-insensitive role check for admin
        if not any(r.name.lower() == 'admin' for r in user.roles):
            return {
                'message': 'Only admins can access this resource',
                'your_roles': [r.name for r in user.roles]
            }, 403
        
        attendances = Attendance.query.all()
        
        return {
            'attendances': [
                {
                    'id': att.id,
                    'user_id': att.user_id,
                    'user_name': att.user.name,
                    'date': att.date.isoformat(),
                    'time': att.time.isoformat(),
                    'location': att.location,
                    'latitude': att.latitude,
                    'longitude': att.longitude,
                    'user_image': att.user_image
                } for att in attendances
            ]
        }, 200

class AdminTrackingResource(Resource):
    @jwt_required()
    def get(self, user_id):
        current_user_id = get_jwt_identity()
        user = User.query.options(db.joinedload(User.roles)).get(current_user_id)
            
        if not user:
            return {'message': 'User not found'}, 404

        # Case-insensitive role check for admin
        if not any(r.name.lower() == 'admin' for r in user.roles):
            return {
                'message': 'Only admins can access this resource',
                'your_roles': [r.name for r in user.roles]
            }, 403
        
        trackings = Tracking.query.filter_by(user_id=user_id).order_by(Tracking.timestamp.desc()).all()
        
        return {
            'trackings': [
                {
                    'id': t.id,
                    'timestamp': t.timestamp.isoformat(),
                    'latitude': t.latitude,
                    'longitude': t.longitude,
                    'accuracy': t.accuracy
                } for t in trackings
            ]
        }, 200

class AdminFaultyMetersResource(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user = User.query.options(db.joinedload(User.roles)).get(current_user_id)
            
        if not user:
            return {'message': 'User not found'}, 404

        # Case-insensitive role check for admin
        if not any(r.name.lower() == 'admin' for r in user.roles):
            return {
                'message': 'Only admins can access this resource',
                'your_roles': [r.name for r in user.roles]
            }, 403
        
        faulty_meters = FaultyMeter.query.all()
        
        return {
            'faulty_meters': [
                {
                    'id': fm.id,
                    'user_id': fm.user_id,
                    'user_name': fm.user.name,
                    'serial_no': fm.serial_no,
                    'meter_image': fm.meter_image,
                    'remark': fm.remark,
                    'status': fm.status,
                    'created_at': fm.created_at.isoformat(),
                    'updated_at': fm.updated_at.isoformat() if fm.updated_at else None
                } for fm in faulty_meters
            ]
        }, 200
    
    @jwt_required()
    def patch(self, meter_id):
        current_user_id = get_jwt_identity()
        user = User.query.options(db.joinedload(User.roles)).get(current_user_id)
            
        if not user:
            return {'message': 'User not found'}, 404

        # Case-insensitive role check for admin
        if not any(r.name.lower() == 'admin' for r in user.roles):
            return {
                'message': 'Only admins can access this resource',
                'your_roles': [r.name for r in user.roles]
            }, 403
        
        data = request.get_json()
        
        if 'status' not in data or data['status'] not in ['Submitted to Godown', 'Returned to Client', 'Pending']:
            return {'message': 'Invalid status update'}, 400
        
        faulty_meter = FaultyMeter.query.get(meter_id)
        if not faulty_meter:
            return {'message': 'Meter report not found'}, 404
        
        faulty_meter.status = data['status']
        db.session.commit()
        
        return {'message': 'Meter status updated successfully'}, 200

class AdminAdverseConditionsResource(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user = User.query.options(db.joinedload(User.roles)).get(current_user_id)
            
        if not user:
            return {'message': 'User not found'}, 404

        # Case-insensitive role check for admin
        if not any(r.name.lower() == 'admin' for r in user.roles):
            return {
                'message': 'Only admins can access this resource',
                'your_roles': [r.name for r in user.roles]
            }, 403
        
        adverse_conditions = AdverseCondition.query.all()
        
        return {
            'adverse_conditions': [
                {
                    'id': ac.id,
                    'user_id': ac.user_id,
                    'user_name': ac.user.name,
                    'condition': ac.condition,
                    'consumer_id': ac.consumer_id,
                    'created_at': ac.created_at.isoformat()
                } for ac in adverse_conditions
            ]
        }, 200