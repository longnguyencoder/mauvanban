"""
Category controller - RESTful API endpoints for category management
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from services import CategoryService
from middleware import admin_required

# Create namespace
category_ns = Namespace('categories', description='Category operations')

# Models
category_model = category_ns.model('Category', {
    'id': fields.String,
    'name': fields.String,
    'slug': fields.String,
    'description': fields.String,
    'parent_id': fields.String,
    'icon': fields.String,
    'display_order': fields.Integer,
    'is_active': fields.Boolean
})

create_category_model = category_ns.model('CreateCategory', {
    'name': fields.String(required=True),
    'description': fields.String,
    'parent_id': fields.String,
    'icon': fields.String,
    'display_order': fields.Integer
})


@category_ns.route('')
class CategoryList(Resource):
    """Category list endpoint"""
    
    @category_ns.doc(description='Get all categories as flat list')
    def get(self):
        """Get all categories"""
        categories = CategoryService.get_all_categories()
        
        return {
            'success': True,
            'data': [cat.to_dict(include_documents=True) for cat in categories]
        }, 200


@category_ns.route('/tree')
class CategoryTree(Resource):
    """Category tree endpoint"""
    
    @category_ns.doc(description='Get categories in tree structure')
    def get(self):
        """Get category tree"""
        tree = CategoryService.get_category_tree()
        
        return {
            'success': True,
            'data': tree
        }, 200


@category_ns.route('/<string:slug>')
class CategoryDetail(Resource):
    """Category detail endpoint"""
    
    @category_ns.doc(description='Get category by slug')
    def get(self, slug):
        """Get category detail"""
        category = CategoryService.get_category_by_slug(slug)
        
        if not category:
            return {
                'success': False,
                'message': 'Category not found'
            }, 404
        
        return {
            'success': True,
            'data': category.to_dict(include_children=True, include_documents=True)
        }, 200


@category_ns.route('/<string:slug>/documents')
class CategoryDocuments(Resource):
    """Category documents endpoint"""
    
    @category_ns.doc(description='Get documents in category')
    def get(self, slug):
        """Get category documents"""
        from services import DocumentService
        
        category = CategoryService.get_category_by_slug(slug)
        
        if not category:
            return {
                'success': False,
                'message': 'Category not found'
            }, 404
        
        # Get pagination params
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        result = DocumentService.list_documents(
            page=page,
            per_page=per_page,
            category_id=category.id
        )
        
        return {
            'success': True,
            'data': result
        }, 200
