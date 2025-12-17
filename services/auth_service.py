"""
Authentication service for user registration, login, and token management
"""
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token
from models import db, User
from email_validator import validate_email, EmailNotValidError


class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    def register(email, password, full_name=None, phone=None):
        """
        Register a new user
        
        Args:
            email: User email
            password: User password
            full_name: User full name (optional)
            phone: User phone (optional)
            
        Returns:
            tuple: (user, error_message)
        """
        try:
            # Validate email
            try:
                valid = validate_email(email)
                email = valid.email
            except EmailNotValidError as e:
                return None, str(e)
            
            # Check if email already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return None, 'Email already registered'
            
            # Validate password
            if len(password) < 6:
                return None, 'Password must be at least 6 characters'
            
            # Create new user
            user = User(
                email=email,
                full_name=full_name,
                phone=phone,
                role='user'
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return user, None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Registration failed: {str(e)}'
    
    @staticmethod
    def login(email, password):
        """
        Login user and generate tokens
        
        Args:
            email: User email
            password: User password
            
        Returns:
            tuple: (user, access_token, refresh_token, error_message)
        """
        try:
            # Find user by email
            user = User.query.filter_by(email=email).first()
            
            if not user:
                return None, None, None, 'Invalid email or password'
            
            # Check password
            if not user.check_password(password):
                return None, None, None, 'Invalid email or password'
            
            # Check if user is active
            if not user.is_active:
                return None, None, None, 'Account is inactive'
            
            # Generate tokens
            access_token = create_access_token(
                identity=user.id,
                additional_claims={'role': user.role}
            )
            refresh_token = create_refresh_token(identity=user.id)
            
            return user, access_token, refresh_token, None
            
        except Exception as e:
            return None, None, None, f'Login failed: {str(e)}'
    
    @staticmethod
    def change_password(user_id, old_password, new_password):
        """
        Change user password
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            user = db.session.get(User, user_id)
            
            if not user:
                return False, 'User not found'
            
            # Verify old password
            if not user.check_password(old_password):
                return False, 'Current password is incorrect'
            
            # Validate new password
            if len(new_password) < 6:
                return False, 'New password must be at least 6 characters'
            
            # Update password
            user.set_password(new_password)
            db.session.commit()
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f'Password change failed: {str(e)}'
    
    @staticmethod
    def update_profile(user_id, full_name=None, phone=None):
        """
        Update user profile
        
        Args:
            user_id: User ID
            full_name: New full name (optional)
            phone: New phone (optional)
            
        Returns:
            tuple: (user, error_message)
        """
        try:
            user = db.session.get(User, user_id)
            
            if not user:
                return None, 'User not found'
            
            # Update fields
            if full_name is not None:
                user.full_name = full_name
            if phone is not None:
                user.phone = phone
            
            db.session.commit()
            
            return user, None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Profile update failed: {str(e)}'
    
    @staticmethod
    def create_admin(email, password, full_name=None):
        """
        Create an admin user (for seeding)
        
        Args:
            email: Admin email
            password: Admin password
            full_name: Admin full name (optional)
            
        Returns:
            tuple: (user, error_message)
        """
        try:
            # Check if email already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return None, 'Email already registered'
            
            # Create admin user
            user = User(
                email=email,
                full_name=full_name,
                role='admin'
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return user, None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Admin creation failed: {str(e)}'
