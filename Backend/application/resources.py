from flask_restful import Api
from .auth import RegisterResource, LoginResource, LogoutResource, TokenRefreshResource
from .installer import AttendanceResource, TrackingResource, FaultyMeterResource, AdverseConditionResource
from .supervisor import (
    SupervisorInstallersResource, SupervisorAttendanceResource,
    SupervisorTrackingResource, SupervisorFaultyMetersResource,
    SupervisorAdverseConditionsResource
)
from .admin import (
    AdminUsersResource, AdminAttendanceResource, AdminTrackingResource,
    AdminFaultyMetersResource, AdminAdverseConditionsResource
)

api = Api()  # Don't pass Resource here

def init_api(app):
    # Register resources
    # Authentication
    api.add_resource(RegisterResource, '/auth/register')
    api.add_resource(LoginResource, '/auth/login')
    api.add_resource(LogoutResource, '/auth/logout')
    api.add_resource(TokenRefreshResource, '/auth/refresh')

    # Installer endpoints
    api.add_resource(AttendanceResource, '/installer/attendance')
    api.add_resource(TrackingResource, '/installer/tracking')
    api.add_resource(FaultyMeterResource, '/installer/faulty-meter')
    api.add_resource(AdverseConditionResource, '/installer/adverse-condition') 

    # Supervisor endpoints
    api.add_resource(SupervisorInstallersResource, '/supervisor/installers')
    api.add_resource(SupervisorAttendanceResource, '/supervisor/attendances')
    api.add_resource(SupervisorTrackingResource, '/supervisor/tracking/<int:installer_id>')
    api.add_resource(SupervisorFaultyMetersResource, 
                    '/supervisor/faulty-meters',
                    '/supervisor/faulty-meters/<int:meter_id>')
    api.add_resource(SupervisorAdverseConditionsResource, '/supervisor/adverse-conditions')

    # Admin endpoints
    api.add_resource(AdminUsersResource, '/admin/users')
    api.add_resource(AdminAttendanceResource, '/admin/attendances')
    api.add_resource(AdminTrackingResource, '/admin/tracking/<int:user_id>')
    api.add_resource(AdminFaultyMetersResource, 
                    '/admin/faulty-meters',
                    '/admin/faulty-meters/<int:meter_id>')
    api.add_resource(AdminAdverseConditionsResource, '/admin/adverse-conditions')
    
    # Initialize the API with the app
    api.init_app(app)