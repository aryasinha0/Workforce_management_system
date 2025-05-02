from datetime import datetime
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User, Attendance, FaultyMeter, AdverseCondition, Tracking
from .database import db
from flask import request

class SupervisorInstallersResource(Resource):
    @jwt_required()
    def get(self):
        try:
            current_user_id = get_jwt_identity()
            
            # Eager load roles to ensure they're available
            user = User.query.options(db.joinedload(User.roles)).get(current_user_id)
            
            if not user:
                return {'message': 'User not found'}, 404
                
            # Case-insensitive role check
            if not any(r.name.lower() == 'supervisor' for r in user.roles):
                return {
                    'message': 'Only supervisors can access this resource',
                    'your_roles': [r.name for r in user.roles]  # Diagnostic info
                }, 403
            
            # Get installers with their last activity
            installers = User.query.filter_by(supervisor_id=current_user_id).all()
            
            return {
                'installers': [
                    {
                        'id': installer.id,
                        'name': installer.name,
                        'phone_number': installer.phone_number
                    }
                    for installer in installers
                ]
            }, 200
            
        except Exception as e:
            return {'message': str(e)}, 500

class SupervisorAttendanceResource(Resource):
    @jwt_required()
    def get(self):
        try:
            current_user_id = get_jwt_identity()
            
            # Eager load roles to ensure they're available
            user = User.query.options(db.joinedload(User.roles)).get(current_user_id)
            
            if not user:
                return {'message': 'User not found'}, 404
                
            # Case-insensitive role check with debug info
            if not any(r.name.lower() == 'supervisor' for r in user.roles):
                return {
                    'message': 'Only supervisors can access this resource',
                    'your_roles': [r.name for r in user.roles],  # Diagnostic info
                    'user_id': current_user_id
                }, 403
            
            # Get installers under this supervisor
            installers = User.query.filter_by(supervisor_id=current_user_id).all()
            
            if not installers:
                return {'message': 'No installers assigned to this supervisor'}, 404
                
            installer_ids = [i.id for i in installers]
            
            # Get attendances with user relationship loaded
            attendances = Attendance.query.options(
                db.joinedload(Attendance.user)
            ).filter(
                Attendance.user_id.in_(installer_ids)
            ).all()
            
            return {
                'attendances': [
                    {
                        'id': att.id,
                        'user_id': att.user_id,
                        'user_name': att.user.name,
                        'date': att.date.isoformat(),
                        'time': att.time.strftime('%H:%M:%S'),
                        'location': att.location,
                        'latitude': att.latitude,
                        'longitude': att.longitude,
                        'user_image': att.user_image,
                        'installer_phone': att.user.phone_number  # Added useful field
                    }
                    for att in attendances
                ]
            }, 200
            
        except Exception as e:
            return {'message': f'Server error: {str(e)}'}, 500

class SupervisorTrackingResource(Resource):
    @jwt_required()
    def get(self, installer_id):
        try:
            current_user_id = get_jwt_identity()
            
            # Eager load roles with the user query
            user = User.query.options(db.joinedload(User.roles)).get(current_user_id)
            
            if not user:
                return {'message': 'User not found', 'status': 'error'}, 404
            
            # Debugging: Print user roles to console
            print(f"User roles: {[role.name for role in user.roles]}")
            
            # Case-insensitive role check with detailed error
            if not any(role.name.lower() == 'supervisor' for role in user.roles):
                return {
                    'message': 'Access denied: Supervisor privileges required',
                    'your_roles': [role.name for role in user.roles],
                    'required_role': 'Supervisor',
                    'status': 'error'
                }, 403
            
            # Verify installer relationship
            installer = db.session.query(User).filter(
                User.id == installer_id,
                User.supervisor_id == current_user_id
            ).first()
            
            if not installer:
                return {
                    'message': 'Installer not found under your supervision',
                    'installer_id': installer_id,
                    'your_supervisor_id': current_user_id,
                    'status': 'error'
                }, 404
            
            # Get tracking data with efficient query
            trackings = Tracking.query.filter_by(
                user_id=installer_id
            ).order_by(
                Tracking.timestamp.desc()
            ).all()
            
            return {
                'status': 'success',
                'installer': {
                    'id': installer.id,
                    'name': installer.name,
                    'phone': installer.phone_number
                },
                'trackings': [
                    {
                        'id': t.id,
                        'timestamp': t.timestamp.isoformat(),
                        'latitude': t.latitude,
                        'longitude': t.longitude,
                        'accuracy': t.accuracy,
                        'location': t.location  # Added location data
                    } for t in trackings
                ],
                'count': len(trackings)
            }, 200
            
        except Exception as e:
            return {
                'message': 'Server error',
                'error': str(e),
                'status': 'error'
            }, 500

class SupervisorFaultyMetersResource(Resource):
    @jwt_required()
    def get(self, meter_id=None):
        current_user_id = get_jwt_identity()
        user = User.query.options(db.joinedload(User.roles)).get(current_user_id)
            
        if not user:
            return {'message': 'User not found'}, 404
            
        # Case-insensitive role check
        if not any(r.name.lower() == 'supervisor' for r in user.roles):
            return {
                'message': 'Only supervisors can access this resource',
                'your_roles': [r.name for r in user.roles]  # Diagnostic info
            }, 403
        # Handle GET /supervisor/faulty-meters (list all)
        if meter_id is None:
            installers = User.query.filter_by(supervisor_id=current_user_id).all()
            installer_ids = [installer.id for installer in installers]
            
            faulty_meters = FaultyMeter.query.filter(FaultyMeter.user_id.in_(installer_ids)).all()
            
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
        
        # Handle GET /supervisor/faulty-meters/<meter_id> (single meter)
        faulty_meter = FaultyMeter.query.get(meter_id)
        if not faulty_meter:
            return {'message': 'Meter report not found'}, 404
        
        if faulty_meter.user.supervisor_id != current_user_id:
            return {'message': 'You can only access meters for your installers'}, 403
        
        return {
            'faulty_meter': {
                'id': faulty_meter.id,
                'user_id': faulty_meter.user_id,
                'user_name': faulty_meter.user.name,
                'serial_no': faulty_meter.serial_no,
                'meter_image': faulty_meter.meter_image,
                'remark': faulty_meter.remark,
                'status': faulty_meter.status,
                'created_at': faulty_meter.created_at.isoformat(),
                'updated_at': faulty_meter.updated_at.isoformat() if faulty_meter.updated_at else None
            }
        }, 200
    
    @jwt_required()
    def patch(self, meter_id):
        try:
            # 1. Authentication & Authorization
            current_user_id = int(get_jwt_identity())  # Convert JWT string to int
            user = User.query.options(db.joinedload(User.roles)).get(current_user_id)

            if not user:
                return {'message': 'User not found'}, 404

            # Case-insensitive role check for supervisor
            if not any(r.name.lower() == 'supervisor' for r in user.roles):
                return {
                    'message': 'Only supervisors can access this resource',
                    'your_roles': [r.name for r in user.roles]
                }, 403

            # 2. Request Validation
            data = request.get_json()
            if not data:
                return {'message': 'No data provided for update'}, 400

            allowed_fields = {'status', 'remark'}
            invalid_fields = set(data.keys()) - allowed_fields
            if invalid_fields:
                return {
                    'message': 'Invalid fields in request',
                    'allowed_fields': list(allowed_fields),
                    'invalid_fields': list(invalid_fields)
                }, 400

            if 'status' in data and data['status'] not in ['Received', 'Not Received']:
                return {
                    'message': 'Invalid status value',
                    'allowed_values': ['Received', 'Not Received']
                }, 400

            # 3. Meter Validation (with eager loading)
            faulty_meter = FaultyMeter.query.options(
                db.joinedload(FaultyMeter.user)
            ).get(meter_id)

            if not faulty_meter:
                return {'message': 'Meter report not found'}, 404

            # 4. Supervisor-Installer Relationship Check (TYPE-SAFE)
            if faulty_meter.user.supervisor_id != current_user_id:  # Now comparing int vs int
                return {
                    'message': 'You can only update meters for your installers',
                    'details': {
                        'meter_user_id': faulty_meter.user_id,
                        'meter_user_supervisor': faulty_meter.user.supervisor_id,
                        'your_id': current_user_id,
                        'type_check': {
                            'jwt_id_type': type(get_jwt_identity()),
                            'db_id_type': type(faulty_meter.user.supervisor_id)
                        }
                    }
                }, 403

            # 5. Update Meter
            for field in allowed_fields:
                if field in data:
                    setattr(faulty_meter, field, data[field])

            faulty_meter.updated_at = datetime.utcnow()
            db.session.commit()

            return {
                'message': 'Meter updated successfully',
                'updated_meter': {
                    'id': faulty_meter.id,
                    'status': faulty_meter.status,
                    'remark': faulty_meter.remark,
                    'updated_at': faulty_meter.updated_at.isoformat()
                }
            }, 200

        except Exception as e:
            db.session.rollback()
            return {
                'message': 'Internal server error',
                'error': str(e),
                'debug_info': {
                    'current_user_id': current_user_id,
                    'meter_id': meter_id
                }
            }, 500



class SupervisorAdverseConditionsResource(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user = User.query.options(db.joinedload(User.roles)).get(current_user_id)
            
        if not user:
            return {'message': 'User not found'}, 404

        # Case-insensitive role check for supervisor
        if not any(r.name.lower() == 'supervisor' for r in user.roles):
            return {
                'message': 'Only supervisors can access this resource',
                'your_roles': [r.name for r in user.roles]
            }, 403
    
        installers = User.query.filter_by(supervisor_id=current_user_id).all()
        installer_ids = [installer.id for installer in installers]
        
        adverse_conditions = AdverseCondition.query.filter(AdverseCondition.user_id.in_(installer_ids)).all()
        
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