"""
Document service for managing documents
"""
from models import db, Document, DocumentGuide, Category, DocumentFile
from sqlalchemy import or_, func


class DocumentService:
    """Service for document operations"""
    
    @staticmethod
    def list_documents(page=1, per_page=20, category_id=None, is_featured=None, 
                      search_query=None, sort_by='created_at', sort_order='desc'):
        """
        List documents with pagination and filters
        
        Args:
            page: Page number
            per_page: Items per page
            category_id: Filter by category
            is_featured: Filter by featured status
            search_query: Search in title and description
            sort_by: Sort field (created_at, views_count, downloads_count, price)
            sort_order: Sort order (asc, desc)
            
        Returns:
            dict: {documents, total, page, per_page, pages}
        """
        query = Document.query.filter_by(is_active=True)
        
        # Apply filters
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if is_featured is not None:
            query = query.filter_by(is_featured=is_featured)
        
        if search_query:
            # Clean and normalize search query
            search_query = search_query.strip()
            
            # Create search pattern for partial matching
            search_pattern = f'%{search_query}%'
            
            # Search in title, description, code, and content
            # Using ilike for case-insensitive search (works with Vietnamese)
            query = query.filter(
                or_(
                    Document.title.ilike(search_pattern),
                    Document.description.ilike(search_pattern),
                    Document.code.ilike(search_pattern),
                    Document.content.ilike(search_pattern)
                )
            )
        
        # Apply sorting
        sort_column = getattr(Document, sort_by, Document.created_at)
        if sort_order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'documents': [doc.to_dict(include_category=True) for doc in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    
    @staticmethod
    def search_documents(query, page=1, per_page=20):
        """
        Search documents
        
        Args:
            query: Search query
            page: Page number
            per_page: Items per page
            
        Returns:
            dict: Search results with pagination
        """
        return DocumentService.list_documents(
            page=page,
            per_page=per_page,
            search_query=query
        )
    
    @staticmethod
    def get_document_by_id(document_id):
        """Get document by ID"""
        return db.session.get(Document, document_id)
    
    @staticmethod
    def get_document_by_slug(slug):
        """Get document by slug"""
        return Document.query.filter_by(slug=slug, is_active=True).first()
    
    @staticmethod
    def create_document(code, title, description, category_id, price=0, 
                       content=None, file_url=None, file_type=None,
                       is_featured=False, meta_keywords=None, meta_description=None,
                       guide_data=None, thumbnail_url=None, files_data=None):
        """
        Create a new document
        
        Args:
            code: Document code (e.g., AB1-01)
            title: Document title
            description: Document description
            category_id: Category ID
            price: Document price
            content: Preview content
            file_url: File URL
            file_type: File type
            is_featured: Featured status
            meta_keywords: SEO keywords
            meta_description: SEO description
            guide_data: Guide data dict (optional)
            
        Returns:
            tuple: (document, error_message)
        """
        try:
            # Verify category exists
            category = db.session.get(Category, category_id)
            if not category:
                return None, 'Category not found'
            
            # Check if code already exists and auto-increment if needed
            original_code = code
            counter = 1
            while Document.query.filter_by(code=code).first():
                code = f"{original_code}-{counter}"
                counter += 1
            
            # Generate unique slug
            from slugify import slugify
            base_slug = slugify(title)
            slug = base_slug
            counter = 1
            
            while Document.query.filter_by(slug=slug).first():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            document = Document(
                code=code,
                title=title,
                description=description,
                category_id=category_id,
                price=price,
                content=content,
                thumbnail_url=thumbnail_url,
                slug=slug  # Set explicitly
            )
            
            db.session.add(document)
            db.session.flush()  # Get document ID
            
            # Create files if provided
            if files_data and isinstance(files_data, list):
                for index, file_data in enumerate(files_data):
                    doc_file = DocumentFile(
                        document_id=document.id,
                        file_url=file_data.get('file_url'),
                        preview_url=file_data.get('preview_url'),
                        file_type=file_data.get('file_type'),
                        original_filename=file_data.get('original_filename'),
                        file_size=file_data.get('file_size'),
                        display_order=index
                    )
                    db.session.add(doc_file)
                    
                    # If this is the first file and document doesn't have file_url, set it from the first file
                    if index == 0 and not document.file_url:
                        document.file_url = file_data.get('file_url')
                        document.file_type = file_data.get('file_type')
            
            # Create guide if provided
            if guide_data:
                guide = DocumentGuide(
                    document_id=document.id,
                    usage_guide=guide_data.get('usage_guide'),
                    filling_guide=guide_data.get('filling_guide'),
                    submission_guide=guide_data.get('submission_guide'),
                    required_documents=guide_data.get('required_documents'),
                    fees_info=guide_data.get('fees_info'),
                    notes=guide_data.get('notes')
                )
                db.session.add(guide)
            
            db.session.commit()
            
            return document, None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Failed to create document: {str(e)}'
    
    @staticmethod
    def update_document(document_id, **kwargs):
        """
        Update document
        
        Args:
            document_id: Document ID
            **kwargs: Fields to update
            
        Returns:
            tuple: (document, error_message)
        """
        try:
            document = db.session.get(Document, document_id)
            
            if not document:
                return None, 'Document not found'
            
            # Update document fields
            allowed_fields = [
                'title', 'description', 'category_id', 'price', 'content',
                'file_url', 'file_type', 'is_featured', 'is_active',
                'meta_keywords', 'meta_description', 'thumbnail_url'
            ]
            
            for field in allowed_fields:
                if field in kwargs:
                    setattr(document, field, kwargs[field])
            
            # Regenerate slug if title changed
            if 'title' in kwargs:
                document.generate_slug()
            
            # Update guide if provided
            if 'guide_data' in kwargs:
                guide_data = kwargs['guide_data']
                if document.guide:
                    # Update existing guide
                    for key, value in guide_data.items():
                        if hasattr(document.guide, key):
                            setattr(document.guide, key, value)
                else:
                    # Create new guide
                    guide = DocumentGuide(
                        document_id=document.id,
                        **guide_data
                    )
                    db.session.add(guide)
            
            db.session.commit()
            
            return document, None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Failed to update document: {str(e)}'
    
    @staticmethod
    def delete_document(document_id):
        """
        Delete document (soft delete)
        
        Args:
            document_id: Document ID
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            document = db.session.get(Document, document_id)
            
            if not document:
                return False, 'Document not found'
            
            # Soft delete
            document.is_active = False
            db.session.commit()
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f'Failed to delete document: {str(e)}'
    
    @staticmethod
    def increment_view(document_id):
        """Increment document view count"""
        try:
            document = db.session.get(Document, document_id)
            if document:
                document.increment_views()
                db.session.commit()
                return True
        except:
            db.session.rollback()
        return False
    
    @staticmethod
    def increment_download(document_id):
        """Increment document download count"""
        try:
            document = db.session.get(Document, document_id)
            if document:
                document.increment_downloads()
                db.session.commit()
                return True
        except:
            db.session.rollback()
        return False
