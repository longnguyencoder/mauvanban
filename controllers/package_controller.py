"""
Package controller - RESTful API endpoints for package management
FIXED: Proper decorator usage
"""
from flask import request
from flask_restx import Namespace, Resource
from services import PackageService, TransactionService
from middleware import token_required

# Create namespace
package_ns = Namespace('packages', description='Package operations')


@package_ns.route('')
class PackageList(Resource):
    """Package list endpoint"""
    
    @package_ns.doc(description='List all packages')
    @package_ns.param('page', 'Page number', type=int, default=1)
    @package_ns.param('per_page', 'Items per page', type=int, default=20)
    def get(self):
        """List packages"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        result = PackageService.list_packages(
            page=page,
            per_page=per_page
        )
        
        return {
            'success': True,
            'data': result
        }, 200


@package_ns.route('/<string:slug>')
class PackageDetail(Resource):
    """Package detail endpoint"""
    
    @package_ns.doc(description='Get package detail by slug')
    def get(self, slug):
        """Get package detail"""
        package = PackageService.get_package_by_slug(slug)
        
        if not package:
            return {
                'success': False,
                'message': 'Package not found'
            }, 404
        
        return {
            'success': True,
            'data': package.to_dict(include_documents=True)
        }, 200


@package_ns.route('/<string:id>/purchase')
class PurchasePackage(Resource):
    """Purchase package endpoint"""
    
    @token_required
    @package_ns.doc(description='Purchase a package', security='Bearer')
    def post(self, current_user, id):
        """Purchase package"""
        transaction, error = TransactionService.purchase_package(
            current_user.id,
            id
        )
        
        if error:
            return {
                'success': False,
                'message': error
            }, 400
        
        return {
            'success': True,
            'message': 'Package purchased successfully',
            'data': transaction.to_dict(include_details=True)
        }, 201
