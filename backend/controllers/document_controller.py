"""
Document controller - RESTful API endpoints for document management
FIXED: Proper decorator usage
"""
from flask import request
from flask_restx import Namespace, Resource
from services import DocumentService, TransactionService, UserService
from middleware import token_required, optional_auth

# Create namespace
document_ns = Namespace('documents', description='Document operations')


@document_ns.route('')
class DocumentList(Resource):
    """Document list endpoint"""
    
    @document_ns.doc(description='List documents with pagination and filters')
    @document_ns.param('page', 'Page number', type=int, default=1)
    @document_ns.param('per_page', 'Items per page', type=int, default=20)
    @document_ns.param('category_id', 'Filter by category ID')
    @document_ns.param('is_featured', 'Filter by featured status', type=bool)
    @document_ns.param('q', 'Search query')  # Changed from 'search' to 'q'
    @document_ns.param('sort_by', 'Sort field', enum=['created_at', 'views_count', 'downloads_count', 'price'])
    @document_ns.param('sort_order', 'Sort order', enum=['asc', 'desc'])
    def get(self):
        """List documents"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category_id = request.args.get('category_id')
        is_featured = request.args.get('is_featured', type=bool)
        search = request.args.get('q')  # Changed from 'search' to 'q'
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        result = DocumentService.list_documents(
            page=page,
            per_page=per_page,
            category_id=category_id,
            is_featured=is_featured,
            search_query=search,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return {
            'success': True,
            'data': result
        }, 200


@document_ns.route('/search')
class DocumentSearch(Resource):
    """Document search endpoint"""
    
    @document_ns.doc(description='Search documents')
    @document_ns.param('q', 'Search query', required=True)
    @document_ns.param('page', 'Page number', type=int, default=1)
    @document_ns.param('per_page', 'Items per page', type=int, default=20)
    def get(self):
        """Search documents"""
        query = request.args.get('q', '')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        if not query:
            return {
                'success': False,
                'message': 'Search query is required'
            }, 400
        
        result = DocumentService.search_documents(
            query=query,
            page=page,
            per_page=per_page
        )
        
        return {
            'success': True,
            'data': result
        }, 200


@document_ns.route('/<string:slug>')
class DocumentDetail(Resource):
    """Document detail endpoint"""
    
    @optional_auth
    @document_ns.doc(description='Get document detail by slug')
    def get(self, current_user, slug):
        """Get document detail"""
        # 1. Try get by slug
        document = DocumentService.get_document_by_slug(slug)
        
        # 2. If not found, check if it's an ID (UUID)
        if not document:
            try:
                import uuid
                # Simple check for UUID format
                uuid_obj = uuid.UUID(slug)
                document = DocumentService.get_document_by_id(slug)
            except ValueError:
                pass
        
        if not document:
            return {
                'success': False,
                'message': 'Document not found'
            }, 404
        
        # Increment view count
        DocumentService.increment_view(document.id)
        
        # Check if user has purchased
        has_purchased = False
        if current_user:
            has_purchased = TransactionService.check_user_purchased_document(
                current_user.id,
                document.id
            )
        
        data = document.to_dict(include_guide=True, include_category=True)
        data['has_purchased'] = has_purchased
        
        return {
            'success': True,
            'data': data
        }, 200


@document_ns.route('/<string:slug>/preview')
class DocumentPreview(Resource):
    """Document preview endpoint"""
    
    @document_ns.doc(description='Get document preview content')
    def get(self, slug):
        """Get document preview"""
        document = DocumentService.get_document_by_slug(slug)
        
        if not document:
            return {
                'success': False,
                'message': 'Document not found'
            }, 404
        
        return {
            'success': True,
            'data': {
                'code': document.code,
                'title': document.title,
                'content': document.content
            }
        }, 200


@document_ns.route('/<string:id>/save')
class SaveDocument(Resource):
    """Save document endpoint"""
    
    @token_required
    @document_ns.doc(description='Save/bookmark document', security='Bearer')
    def post(self, current_user, id):
        """Save document"""
        saved_doc, error = UserService.save_document(current_user.id, id)
        
        if error:
            return {
                'success': False,
                'message': error
            }, 400
        
        return {
            'success': True,
            'message': 'Document saved successfully'
        }, 201
    
    @token_required
    @document_ns.doc(description='Unsave/unbookmark document', security='Bearer')
    def delete(self, current_user, id):
        """Unsave document"""
        success, error = UserService.unsave_document(current_user.id, id)
        
        if error:
            return {
                'success': False,
                'message': error
            }, 400
        
        return {
            'success': True,
            'message': 'Document unsaved successfully'
        }, 200


@document_ns.route('/<string:id>/download')
class DownloadDocument(Resource):
    """Download document endpoint"""
    
    @token_required
    @document_ns.doc(description='Purchase and download document', security='Bearer')
    def post(self, current_user, id):
        """Download document"""
        # Check if already purchased
        has_purchased = TransactionService.check_user_purchased_document(
            current_user.id,
            id
        )
        
        if not has_purchased:
            # Purchase document
            transaction, error = TransactionService.purchase_document(
                current_user.id,
                id
            )
            
            if error:
                return {
                    'success': False,
                    'message': error
                }, 400
        
        # Increment download count
        DocumentService.increment_download(id)
        
        # Get document
        document = DocumentService.get_document_by_id(id)
        
        return {
            'success': True,
            'message': 'Document ready for download',
            'data': {
                'file_url': document.file_url,
                'file_type': document.file_type
            }
        }, 200


@document_ns.route('/<string:id>/report')
class ReportDocument(Resource):
    """Report document endpoint"""
    
    @token_required
    @document_ns.doc(description='Report document issue', security='Bearer')
    def post(self, current_user, id):
        """Report document"""
        data = request.json
        reason = data.get('reason', '')
        
        report, error = UserService.report_document(
            current_user.id,
            id,
            reason
        )
        
        if error:
            return {
                'success': False,
                'message': error
            }, 400
        
        return {
            'success': True,
            'message': 'Report submitted successfully',
            'data': report.to_dict()
        }, 201
