"""
Authentication controller - RESTful API endpoints for user authentication
FIXED: Proper decorator usage
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_refresh_token, jwt_required, get_jwt_identity, create_access_token, get_jwt
from services import AuthService
from middleware import token_required

# Create namespace
auth_ns = Namespace('auth', description='Authentication operations')

# Request/Response models
register_model = auth_ns.model('Register', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
    'full_name': fields.String(description='Full name'),
    'phone': fields.String(description='Phone number')
})

login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

change_password_model = auth_ns.model('ChangePassword', {
    'old_password': fields.String(required=True, description='Current password'),
    'new_password': fields.String(required=True, description='New password')
})

update_profile_model = auth_ns.model('UpdateProfile', {
    'full_name': fields.String(description='Full name'),
    'phone': fields.String(description='Phone number')
})


@auth_ns.route('/register')
class Register(Resource):
    """User registration endpoint"""
    
    @auth_ns.expect(register_model)
    @auth_ns.doc(description='Register a new user account')
    def post(self):
        """Register new user"""
        data = request.json
        
        user, error = AuthService.register(
            email=data.get('email'),
            password=data.get('password'),
            full_name=data.get('full_name'),
            phone=data.get('phone')
        )
        
        if error:
            return {
                'success': False,
                'message': error
            }, 400
        
        return {
            'success': True,
            'message': 'Registration successful',
            'data': user.to_dict()
        }, 201


@auth_ns.route('/login')
class Login(Resource):
    """User login endpoint"""
    
    @auth_ns.expect(login_model)
    @auth_ns.doc(description='Login and receive access tokens')
    def post(self):
        """Login user"""
        data = request.json
        
        user, access_token, refresh_token, error = AuthService.login(
            email=data.get('email'),
            password=data.get('password')
        )
        
        if error:
            return {
                'success': False,
                'message': error
            }, 401
        
        return {
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }, 200


@auth_ns.route('/refresh')
class RefreshToken(Resource):
    """Token refresh endpoint"""
    
    @jwt_required(refresh=True)
    @auth_ns.doc(description='Refresh access token using refresh token', security='Bearer')
    def post(self):
        """Refresh access token"""
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        new_access_token = create_access_token(
            identity=user_id,
            additional_claims={'role': claims.get('role', 'user')}
        )
        
        return {
            'success': True,
            'data': {
                'access_token': new_access_token
            }
        }, 200


@auth_ns.route('/me')
class Me(Resource):
    """Current user endpoint"""
    
    @token_required
    @auth_ns.doc(description='Get current user information', security='Bearer')
    def get(self, current_user):
        """Get current user info"""
        return {
            'success': True,
            'data': current_user.to_dict(include_sensitive=True)
        }, 200


@auth_ns.route('/profile')
class Profile(Resource):
    """User profile endpoint"""
    
    @token_required
    @auth_ns.expect(update_profile_model)
    @auth_ns.doc(description='Update user profile', security='Bearer')
    def put(self, current_user):
        """Update profile"""
        data = request.json
        
        user, error = AuthService.update_profile(
            user_id=current_user.id,
            full_name=data.get('full_name'),
            phone=data.get('phone')
        )
        
        if error:
            return {
                'success': False,
                'message': error
            }, 400
        
        return {
            'success': True,
            'message': 'Profile updated successfully',
            'data': user.to_dict()
        }, 200


@auth_ns.route('/change-password')
class ChangePassword(Resource):
    """Change password endpoint"""
    
    @token_required
    @auth_ns.expect(change_password_model)
    @auth_ns.doc(description='Change user password', security='Bearer')
    def post(self, current_user):
        """Change password"""
        data = request.json
        
        success, error = AuthService.change_password(
            user_id=current_user.id,
            old_password=data.get('old_password'),
            new_password=data.get('new_password')
        )
        
        if error:
            return {
                'success': False,
                'message': error
            }, 400
        
        return {
            'success': True,
            'message': 'Password changed successfully'
        }, 200
