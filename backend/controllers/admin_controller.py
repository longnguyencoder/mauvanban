"""
Admin controller - RESTful API endpoints for admin operations
FIXED: Proper decorator usage
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from services import CategoryService, DocumentService, PackageService, UserService
from middleware import admin_required

# Create namespace
admin_ns = Namespace('admin', description='Admin operations')

# Request models for Swagger UI
create_category_model = admin_ns.model('CreateCategory', {
    'name': fields.String(required=True, description='Category name'),
    'description': fields.String(description='Category description'),
    'parent_id': fields.String(description='Parent category ID'),
    'icon': fields.String(description='Icon name'),
    'display_order': fields.Integer(description='Display order', default=0)
})

create_document_model = admin_ns.model('CreateDocument', {
    'code': fields.String(required=True, description='Document code (e.g., HD-01)'),
    'title': fields.String(required=True, description='Document title'),
    'description': fields.String(description='Document description'),
    'category_id': fields.String(required=True, description='Category ID'),
    'price': fields.Float(description='Price in VND', default=0),
    'content': fields.String(description='Document content/preview'),
    'file_url': fields.String(description='File URL'),
    'file_type': fields.String(description='File type (docx, pdf, etc.)'),
    'is_featured': fields.Boolean(description='Featured status', default=False),
    'meta_keywords': fields.String(description='SEO keywords'),
    'meta_description': fields.String(description='SEO description')
})

document_guide_model = admin_ns.model('DocumentGuide', {
    'usage_guide': fields.String(description='Usage guide'),
    'filling_guide': fields.String(description='Filling guide'),
    'submission_guide': fields.String(description='Submission guide'),
    'required_documents': fields.String(description='Required documents'),
    'fees_info': fields.String(description='Fees information'),
    'notes': fields.String(description='Additional notes')
})

create_document_with_guide_model = admin_ns.model('CreateDocumentWithGuide', {
    'code': fields.String(required=True, description='Document code'),
    'title': fields.String(required=True, description='Document title'),
    'description': fields.String(description='Document description'),
    'category_id': fields.String(required=True, description='Category ID'),
    'price': fields.Float(description='Price in VND', default=0),
    'content': fields.String(description='Document content'),
    'file_url': fields.String(description='File URL'),
    'file_type': fields.String(description='File type'),
    'is_featured': fields.Boolean(description='Featured', default=False),
    'meta_keywords': fields.String(description='SEO keywords'),
    'meta_description': fields.String(description='SEO description'),
    'guide': fields.Nested(document_guide_model, description='Document guide')
})

create_package_model = admin_ns.model('CreatePackage', {
    'name': fields.String(required=True, description='Package name'),
    'description': fields.String(description='Package description'),
    'price': fields.Float(required=True, description='Package price'),
    'discount_percent': fields.Float(description='Discount percentage', default=0),
    'document_ids': fields.List(fields.String, description='List of document IDs')
})

adjust_balance_model = admin_ns.model('AdjustBalance', {
    'amount': fields.Float(required=True, description='Amount to add/subtract')
})

update_report_model = admin_ns.model('UpdateReport', {
    'status': fields.String(required=True, description='Report status', enum=['pending', 'reviewing', 'resolved', 'rejected']),
    'admin_note': fields.String(description='Admin note')
})


# ============ CATEGORY MANAGEMENT ============

@admin_ns.route('/categories')
class AdminCategoryList(Resource):
    """Admin category list endpoint"""
    
    @admin_required
    @admin_ns.expect(create_category_model)
    @admin_ns.doc(description='Create new category', security='Bearer')
    def post(self, current_user):
        """Create category"""
        data = request.json
        
        category, error = CategoryService.create_category(
            name=data.get('name'),
            description=data.get('description'),
            parent_id=data.get('parent_id'),
            icon=data.get('icon'),
            display_order=data.get('display_order', 0)
        )
        
        if error:
            return {'success': False, 'message': error}, 400
        
        return {
            'success': True,
            'message': 'Category created successfully',
            'data': category.to_dict()
        }, 201


@admin_ns.route('/categories/<string:id>')
class AdminCategoryDetail(Resource):
    """Admin category detail endpoint"""
    
    @admin_required
    @admin_ns.doc(description='Get category by ID', security='Bearer')
    def get(self, current_user, id):
        """Get category by ID"""
        category = CategoryService.get_category_by_id(id)
        
        if not category:
            return {'success': False, 'message': 'Category not found'}, 404
            
        return {
            'success': True,
            'data': category.to_dict(include_children=True)
        }, 200

    @admin_required
    @admin_ns.doc(description='Update category', security='Bearer')
    def put(self, current_user, id):
        """Update category"""
        data = request.json
        
        category, error = CategoryService.update_category(
            category_id=id,
            **data
        )
        
        if error:
            return {'success': False, 'message': error}, 400
        
        return {
            'success': True,
            'message': 'Category updated successfully',
            'data': category.to_dict()
        }, 200
    
    @admin_required
    @admin_ns.doc(description='Delete category', security='Bearer')
    def delete(self, current_user, id):
        """Delete category"""
        success, error = CategoryService.delete_category(id)
        
        if error:
            return {'success': False, 'message': error}, 400
        
        return {
            'success': True,
            'message': 'Category deleted successfully'
        }, 200


# ============ DOCUMENT MANAGEMENT ============

@admin_ns.route('/documents/json')
class AdminDocumentCreateJSON(Resource):
    """Admin document creation (JSON only - for Swagger UI)"""
    
    @admin_required
    @admin_ns.expect(create_document_with_guide_model)
    @admin_ns.doc(description='Create document (JSON only - use /documents for file upload)', security='Bearer')
    def post(self, current_user):
        """Create document with JSON data (no file upload)
        
        Use this endpoint in Swagger UI to create documents without file upload.
        For file upload, use POST /admin/documents in Postman with form-data.
        """
        data = request.json
        
        document, error = DocumentService.create_document(
            code=data.get('code'),
            title=data.get('title'),
            description=data.get('description'),
            category_id=data.get('category_id'),
            price=data.get('price', 0),
            content=data.get('content'),
            file_url=data.get('file_url'),
            file_type=data.get('file_type'),
            thumbnail_url=data.get('thumbnail_url'),
            is_featured=data.get('is_featured', False),
            meta_keywords=data.get('meta_keywords'),
            meta_description=data.get('meta_description'),
            guide_data=data.get('guide')
        )
        
        if error:
            return {'success': False, 'message': error}, 400
        
        return {
            'success': True,
            'message': 'Document created successfully',
            'data': document.to_dict(include_guide=True)
        }, 201


@admin_ns.route('/documents')
class AdminDocumentList(Resource):
    """Admin document list endpoint"""
    
    @admin_required
    @admin_ns.doc(
        description='Create new document (supports file upload)',
        security='Bearer',
        params={
            'file': 'Document file (PDF, DOC, DOCX, XLS, XLSX) - Optional',
            'code': 'Document code (e.g., HD-01) - Required',
            'title': 'Document title - Required',
            'category_id': 'Category ID - Required',
            'description': 'Document description',
            'price': 'Price in VND (default: 0)',
            'content': 'Document preview content',
            'is_featured': 'Featured status (true/false)',
            'meta_keywords': 'SEO keywords',
            'meta_description': 'SEO description',
            'guide': 'JSON string with guide data: {"usage_guide":"...","filling_guide":"...","submission_guide":"...","required_documents":"...","fees_info":"...","notes":"..."}'
        },
        consumes=['multipart/form-data', 'application/json']
    )
    def post(self, current_user):
        """Create document with optional file upload
        
        **Two ways to use this endpoint:**
        
        **Method 1: With file upload (multipart/form-data)**
        - Use form-data in Postman/frontend
        - Add file field with PDF/Word/Excel file
        - Add other fields as text
        - guide field should be JSON string
        
        **Method 2: Without file (application/json)**
        - Use JSON body
        - Provide file_url if you uploaded file separately
        
        **Example form-data:**
        ```
        file: [select PDF file]
        code: HD-01
        title: Hợp đồng thuê nhà
        category_id: 99820a30-a4ff-47c8-832f-c7e3fe0455b5
        price: 20000
        description: Mẫu hợp đồng...
        content: CỘNG HÒA XÃ HỘI CHỦ NGHĨA...
        is_featured: true
        guide: {"usage_guide":"Sử dụng khi...","filling_guide":"Điền..."}
        ```
        """
        import os
        from werkzeug.utils import secure_filename
        from flask import current_app
        
        # Check if request has file
        has_file = 'file' in request.files
        
        
        # Check if request has files
        has_files = 'file' in request.files or 'files' in request.files or 'files[]' in request.files
        
        files_data = []
        
        if has_files:
            # Handle multipart/form-data
            # Get list of files (support both 'file', 'files', and 'files[]')
            files = request.files.getlist('file') + request.files.getlist('files') + request.files.getlist('files[]')
            
            # Filter empty files
            files = [f for f in files if f.filename != '']
            
            # Get form data
            data = {
                'code': request.form.get('code'),
                'title': request.form.get('title'),
                'description': request.form.get('description'),
                'category_id': request.form.get('category_id'),
                'price': float(request.form.get('price', 0)),
                'content': request.form.get('content'),
                'file_type': request.form.get('file_type'),
                'is_featured': request.form.get('is_featured', 'false').lower() == 'true',
                'meta_keywords': request.form.get('meta_keywords'),
                'meta_description': request.form.get('meta_description'),
                'thumbnail_url': request.form.get('thumbnail_url')
            }
            
            # Handle guide data (JSON string in form)
            import json
            guide_json = request.form.get('guide')
            if guide_json:
                try:
                    data['guide'] = json.loads(guide_json)
                except:
                    data['guide'] = None
            
            # Process each file
            for file in files:
                if file and file.filename:
                    # Validate file
                    allowed_extensions = {'pdf', 'doc', 'docx', 'xls', 'xlsx'}
                    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                    
                    if file_ext not in allowed_extensions:
                        return {
                            'success': False,
                            'message': f'Invalid file type: {file.filename}. Allowed: {", ".join(allowed_extensions)}'
                        }, 400
                    
                    # Generate unique filename
                    import uuid
                    from datetime import datetime
                    unique_filename = f"{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
                    
                    # Save file
                    upload_folder = current_app.config['UPLOAD_FOLDER']
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    file_path = os.path.join(upload_folder, unique_filename)
                    file.save(file_path)
                    
                    # Generate preview
                    from services import PreviewService
                    preview_url = PreviewService.generate_preview(file_path, file.filename)
                    
                    # File info
                    file_info = {
                        'file_url': f"/uploads/documents/{unique_filename}",
                        'file_type': file_ext,
                        'original_filename': secure_filename(file.filename),
                        'file_size': os.path.getsize(file_path),
                        'preview_url': preview_url
                    }
                    
                    files_data.append(file_info)
            
            # Set legacy fields for backward compatibility (using the first file)
            if files_data:
                data['file_url'] = files_data[0]['file_url']
                data['file_type'] = files_data[0]['file_type']
                
                # Auto-set thumbnail from preview if not provided
                if not data.get('thumbnail_url') and files_data[0].get('preview_url'):
                     data['thumbnail_url'] = files_data[0]['preview_url']
            
        else:
            # Handle JSON data
            data = request.json
            files_data = data.get('files_data', [])
        
        # Create document
        document, error = DocumentService.create_document(
            code=data.get('code'),
            title=data.get('title'),
            description=data.get('description'),
            category_id=data.get('category_id'),
            price=data.get('price', 0),
            content=data.get('content'),
            file_url=data.get('file_url'),
            file_type=data.get('file_type'),
            thumbnail_url=data.get('thumbnail_url'),
            is_featured=data.get('is_featured', False),
            meta_keywords=data.get('meta_keywords'),
            meta_description=data.get('meta_description'),
            guide_data=data.get('guide'),
            files_data=files_data
        )
        
        if error:
            return {'success': False, 'message': error}, 400
        
        return {
            'success': True,
            'message': 'Document created successfully',
            'data': document.to_dict(include_guide=True)
        }, 201

    @admin_required
    @admin_ns.doc(description='List all documents for admin', security='Bearer')
    @admin_ns.param('page', 'Page number', type=int, default=1)
    @admin_ns.param('per_page', 'Items per page', type=int, default=20)
    @admin_ns.param('search', 'Search query')
    def get(self, current_user):
        """List all documents"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search')
        
        # Use DocumentService to list documents
        result = DocumentService.list_documents(
            page=page,
            per_page=per_page,
            search_query=search,
            sort_by='created_at',
            sort_order='desc'
        )
        
        return {
            'success': True,
            'data': result
        }, 200



@admin_ns.route('/documents/<string:id>')
class AdminDocumentDetail(Resource):
    """Admin document detail endpoint"""
    
    @admin_required
    @admin_ns.doc(description='Update document', security='Bearer')
    def put(self, current_user, id):
        """Update document"""
        data = request.json
        
        if 'thumbnail_url' in data:
             # Ensure thumbnail_url is passed if present
             pass 

        document, error = DocumentService.update_document(id, **data)
        
        if error:
            return {'success': False, 'message': error}, 400
        
        return {
            'success': True,
            'message': 'Document updated successfully',
            'data': document.to_dict(include_guide=True)
        }, 200
    
    @admin_required
    @admin_ns.doc(description='Delete document', security='Bearer')
    def delete(self, current_user, id):
        """Delete document"""
        success, error = DocumentService.delete_document(id)
        
        if error:
            return {'success': False, 'message': error}, 400
        
        return {
            'success': True,
            'message': 'Document deleted successfully'
        }, 200


# ============ PACKAGE MANAGEMENT ============

@admin_ns.route('/packages')
class AdminPackageList(Resource):
    """Admin package list endpoint"""
    
    @admin_required
    @admin_ns.expect(create_package_model)
    @admin_ns.doc(description='Create new package', security='Bearer')
    def post(self, current_user):
        """Create package"""
        data = request.json
        
        package, error = PackageService.create_package(
            name=data.get('name'),
            description=data.get('description'),
            price=data.get('price'),
            discount_percent=data.get('discount_percent', 0),
            document_ids=data.get('document_ids', [])
        )
        
        if error:
            return {'success': False, 'message': error}, 400
        
        return {
            'success': True,
            'message': 'Package created successfully',
            'data': package.to_dict(include_documents=True)
        }, 201


@admin_ns.route('/packages/<string:id>')
class AdminPackageDetail(Resource):
    """Admin package detail endpoint"""
    
    @admin_required
    @admin_ns.doc(description='Update package', security='Bearer')
    def put(self, current_user, id):
        """Update package"""
        data = request.json
        
        package, error = PackageService.update_package(id, **data)
        
        if error:
            return {'success': False, 'message': error}, 400
        
        return {
            'success': True,
            'message': 'Package updated successfully',
            'data': package.to_dict(include_documents=True)
        }, 200
    
    @admin_required
    @admin_ns.doc(description='Delete package', security='Bearer')
    def delete(self, current_user, id):
        """Delete package"""
        success, error = PackageService.delete_package(id)
        
        if error:
            return {'success': False, 'message': error}, 400
        
        return {
            'success': True,
            'message': 'Package deleted successfully'
        }, 200


@admin_ns.route('/packages/<string:package_id>/documents/<string:document_id>')
class AdminPackageDocuments(Resource):
    """Admin package documents endpoint"""
    
    @admin_required
    @admin_ns.doc(description='Add document to package', security='Bearer')
    def post(self, current_user, package_id, document_id):
        """Add document to package"""
        success, error = PackageService.add_document_to_package(
            package_id,
            document_id
        )
        
        if error:
            return {'success': False, 'message': error}, 400
        
        return {
            'success': True,
            'message': 'Document added to package'
        }, 200
    
    @admin_required
    @admin_ns.doc(description='Remove document from package', security='Bearer')
    def delete(self, current_user, package_id, document_id):
        """Remove document from package"""
        success, error = PackageService.remove_document_from_package(
            package_id,
            document_id
        )
        
        if error:
            return {'success': False, 'message': error}, 400
        
        return {
            'success': True,
            'message': 'Document removed from package'
        }, 200


# ============ USER MANAGEMENT ============

create_user_model = admin_ns.model('CreateUser', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
    'full_name': fields.String(description='Full name'),
    'phone_number': fields.String(description='Phone number'),
    'role': fields.String(description='User role (admin/user)', default='user'),
    'is_active': fields.Boolean(description='Active status', default=True)
})

@admin_ns.route('/users')
class AdminUserList(Resource):
    """Admin user list endpoint"""
    
    @admin_required
    @admin_ns.doc(description='Get all users', security='Bearer')
    @admin_ns.param('page', 'Page number', type=int, default=1)
    @admin_ns.param('per_page', 'Items per page', type=int, default=20)
    @admin_ns.param('role', 'Filter by role', enum=['admin', 'user'])
    @admin_ns.param('is_active', 'Filter by active status', type=bool)
    def get(self, current_user):
        """Get all users"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        role = request.args.get('role')
        is_active = request.args.get('is_active', type=bool)
        
        result = UserService.get_all_users(
            page=page,
            per_page=per_page,
            role=role,
            is_active=is_active
        )
        
        return {
            'success': True,
            'data': result
        }, 200

    @admin_required
    @admin_ns.expect(create_user_model)
    @admin_ns.doc(description='Create new user', security='Bearer')
    def post(self, current_user):
        """Create new user"""
        data = request.json
        
        user, error = UserService.create_user(
            email=data.get('email'),
            password=data.get('password'),
            full_name=data.get('full_name'),
            phone=data.get('phone_number'),
            role=data.get('role', 'user'),
            is_active=data.get('is_active', True)
        )
        
        if error:
            return {'success': False, 'message': error}, 400
            
        return {
            'success': True,
            'message': 'User created successfully',
            'data': user.to_dict(include_sensitive=True)
        }, 201


@admin_ns.route('/users/<string:id>/toggle-active')
class AdminToggleUserActive(Resource):
    """Admin toggle user active endpoint"""
    
    @admin_required
    @admin_ns.doc(description='Toggle user active status', security='Bearer')
    def put(self, current_user, id):
        """Toggle user active"""
        user, error = UserService.toggle_user_active(id)
        
        if error:
            return {'success': False, 'message': error}, 400
        
        return {
            'success': True,
            'message': 'User status updated',
            'data': user.to_dict()
        }, 200


@admin_ns.route('/users/<string:id>/balance')
class AdminAdjustBalance(Resource):
    """Admin adjust balance endpoint"""
    
    @admin_required
    @admin_ns.expect(adjust_balance_model)
    @admin_ns.doc(description='Adjust user balance', security='Bearer')
    def put(self, current_user, id):
        """Adjust balance"""
        data = request.json
        amount = data.get('amount', 0)
        
        user, error = UserService.adjust_user_balance(id, amount)
        
        if error:
            return {'success': False, 'message': error}, 400
        
        return {
            'success': True,
            'message': 'Balance adjusted successfully',
            'data': user.to_dict(include_sensitive=True)
        }, 200


@admin_ns.route('/users/<string:id>')
class AdminUserDetail(Resource):
    """Admin user detail endpoint"""
    
    @admin_required
    @admin_ns.doc(description='Get user details', security='Bearer')
    def get(self, current_user, id):
        """Get user details"""
        user, error = UserService.get_user_by_id(id)
        
        if error:
            return {'success': False, 'message': error}, 404
            
        return {
            'success': True,
            'data': user.to_dict(include_sensitive=True)
        }, 200

    @admin_required
    @admin_ns.doc(description='Update user profile', security='Bearer')
    def put(self, current_user, id):
        """Update user profile"""
        data = request.json
        
        user, error = UserService.update_user_profile(
            id,
            full_name=data.get('full_name'),
            email=data.get('email'),
            phone_number=data.get('phone_number'),
            role=data.get('role')
        )
        
        if error:
            return {'success': False, 'message': error}, 400
        
        return {
            'success': True,
            'message': 'User updated successfully',
            'data': user.to_dict(include_sensitive=True)
        }, 200
    
    @admin_required
    @admin_ns.doc(description='Delete user', security='Bearer')
    def delete(self, current_user, id):
        """Delete user"""
        success, error = UserService.delete_user(id)
        
        if error:
            return {'success': False, 'message': error}, 400
        
        return {
            'success': True,
            'message': 'User deleted successfully'
        }, 200


# ============ REPORTS MANAGEMENT ============

@admin_ns.route('/reports')
class AdminReportList(Resource):
    """Admin report list endpoint"""
    
    @admin_required
    @admin_ns.doc(description='Get all reports', security='Bearer')
    @admin_ns.param('page', 'Page number', type=int, default=1)
    @admin_ns.param('per_page', 'Items per page', type=int, default=20)
    @admin_ns.param('status', 'Filter by status', enum=['pending', 'reviewing', 'resolved', 'rejected'])
    def get(self, current_user):
        """Get all reports"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        
        result = UserService.get_all_reports(
            page=page,
            per_page=per_page,
            status=status
        )
        
        return {
            'success': True,
            'data': result
        }, 200


@admin_ns.route('/reports/<string:id>')
class AdminReportDetail(Resource):
    """Admin report detail endpoint"""
    
    @admin_required
    @admin_ns.expect(update_report_model)
    @admin_ns.doc(description='Update report status', security='Bearer')
    def put(self, current_user, id):
        """Update report"""
        data = request.json
        
        report, error = UserService.update_report_status(
            id,
            data.get('status'),
            data.get('admin_note')
        )
        
        if error:
            return {'success': False, 'message': error}, 400
        
        return {
            'success': True,
            'message': 'Report updated successfully',
            'data': report.to_dict(include_details=True)
        }, 200


@admin_ns.route('/stats')
class AdminStats(Resource):
    """Admin dashboard statistics"""
    
    @admin_required
    @admin_ns.doc(description='Get dashboard statistics', security='Bearer')
    def get(self, current_user):
        """Get dashboard stats"""
        from models import Document, User, Transaction, Category, db
        from sqlalchemy import func
        from datetime import datetime, time

        # 1. Total Documents
        total_documents = Document.query.count()

        # 2. Total Users
        total_users = User.query.count()

        # New users today (robust date range query)
        today_start = datetime.combine(datetime.utcnow().date(), time.min)
        new_users_today = User.query.filter(User.created_at >= today_start).count()

        # 3. Revenue (Total successful transactions of type 'topup')
        total_revenue = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.transaction_type == 'topup',
            Transaction.status == 'completed'
        ).scalar() or 0

        # 4. Total Views/Downloads
        total_views = db.session.query(func.sum(Document.views_count)).scalar() or 0
        total_downloads = db.session.query(func.sum(Document.downloads_count)).scalar() or 0

        return {
            'success': True,
            'data': {
                'total_documents': total_documents,
                'total_users': total_users,
                'new_users_today': new_users_today,
                'total_revenue': float(total_revenue),
                'total_views': int(total_views),
                'total_downloads': int(total_downloads)
            }
        }, 200
