class Config():
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class LocalDevelopmentConfig(Config):
    # configurations for db
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.sqlite3"
    DEBUG = True

    # configurations for security
    SECRET_KEY = "this-is-a-secret-key"   # hash user credentials and use in session
    SECURITY_PASSWORD_HASH = "bcrypt"            # mechanism to hash credentials and store in database
    SECURITY_PASSWORD_SALT = "this-is-a-salt-key" # String that bcrypt uses to hash the credentials
    WTF_CSRF_ENABLED = False        # only for forms (frontend)
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"
    