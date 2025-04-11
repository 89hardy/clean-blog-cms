from flask_login import UserMixin
from werkzeug.security import check_password_hash
from flask import current_app
from config.config import Config

class User(UserMixin):
    """
    User model for authentication.
    Implements Flask-Login's UserMixin for session management.
    Currently supports a single admin user defined in configuration.
    """
    def __init__(self, username):
        self.username = username
        self.id = username
    
    @staticmethod
    def check_credentials(username, password):
        """Check if the provided credentials are valid."""
        return (username == Config.ADMIN_USERNAME and 
                password == Config.ADMIN_PASSWORD)

def init_login_manager(login_manager):
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by user_id."""
        if user_id == Config.ADMIN_USERNAME:
            return User(user_id)
        return None 