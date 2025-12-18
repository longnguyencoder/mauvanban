"""
Controllers package initialization
"""
from flask_restx import Api

# Create API instance with JWT authorization
authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'JWT Authorization header using the Bearer scheme. Example: "Bearer {token}"'
    }
}

api = Api(
    version='1.0',
    title='Mẫu Văn Bản API',
    description='RESTful API for Document Management System',
    doc='/api/docs',
    prefix='/api',
    authorizations=authorizations,
    security='Bearer'
)

# Import namespaces after api creation to avoid circular imports
from .auth_controller import auth_ns
from .category_controller import category_ns
from .document_controller import document_ns
from .package_controller import package_ns
from .user_controller import user_ns
from .admin_controller import admin_ns
from .admin_controller import admin_ns
from .upload_controller import upload_ns
from .contact_controller import contact_ns
from .sepay_controller import sepay_ns

# Add namespaces
api.add_namespace(auth_ns, path='/auth')
api.add_namespace(category_ns, path='/categories')
api.add_namespace(document_ns, path='/documents')
api.add_namespace(package_ns, path='/packages')
api.add_namespace(user_ns, path='/user')
api.add_namespace(admin_ns, path='/admin')
api.add_namespace(upload_ns, path='/upload')
api.add_namespace(contact_ns, path='/contact')
api.add_namespace(sepay_ns, path='/sepay')

__all__ = ['api']
