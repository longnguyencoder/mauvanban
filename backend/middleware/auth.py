"""
Authentication middleware for JWT token validation and role-based access control
"""
from functools import wraps
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from models import db, User


def token_required(fn):
    """
    Decorator to require valid JWT token
    Usage: @token_required
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            # Get user from database
            user = db.session.get(User, user_id)
            
            if not user:
                return {
                    'success': False,
                    'message': 'User not found'
                }, 404
            
            if not user.is_active:
                return {
                    'success': False,
                    'message': 'User account is inactive'
                }, 403
            
            # Pass user to the route function
            return fn(*args, current_user=user, **kwargs)
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': 'Invalid or expired token',
                'error': str(e)
            }, 401
    
    return wrapper


def admin_required(fn):
    """
    Decorator to require admin role
    Usage: @admin_required
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            # Get user from database
            user = db.session.get(User, user_id)
            
            if not user:
                return {
                    'success': False,
                    'message': 'User not found'
                }, 404
            
            if not user.is_active:
                return {
                    'success': False,
                    'message': 'User account is inactive'
                }, 403
            
            if not user.is_admin():
                return {
                    'success': False,
                    'message': 'Admin access required'
                }, 403
            
            # Pass user to the route function
            return fn(*args, current_user=user, **kwargs)
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': 'Invalid or expired token',
                'error': str(e)
            }, 401
    
    return wrapper


def optional_auth(fn):
    """
    Decorator for optional authentication
    Provides current_user if token is present, None otherwise
    Usage: @optional_auth
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            
            current_user = None
            if user_id:
                current_user = db.session.get(User, user_id)
            
            return fn(*args, current_user=current_user, **kwargs)
            
        except Exception:
            # If token verification fails, continue without user
            db.session.rollback()
            return fn(*args, current_user=None, **kwargs)
    
    return wrapper
