class Config():
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class LocalDevelopmentConfig(Config):
    # Database
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.sqlite3"
    DEBUG = True

    # Security (for Flask-Security-Too)
    SECRET_KEY = "this-is-a-secret-key"
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_PASSWORD_SALT = "this-is-a-salt-key"
    WTF_CSRF_ENABLED = False  # Only needed for forms

    # JWT (for Flask-JWT-Extended)
    JWT_SECRET_KEY = "your-very-secret-key"  # Must match Flask-Security's SECRET_KEY?
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 86400  # 1 day
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"  # Standard
    JWT_HEADER_TYPE = "Bearer"  # Standard

    # Disable Flask-Security's token auth (use only JWT)
    SECURITY_TOKEN_AUTHENTICATION_HEADER = None  # 👈 Critical fix