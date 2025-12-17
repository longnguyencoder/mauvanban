"""
Package service for managing document packages
"""
from models import db, DocumentPackage, PackageDocument, Document


class PackageService:
    """Service for document package operations"""
    
    @staticmethod
    def list_packages(page=1, per_page=20, is_active=True):
        """
        List packages with pagination
        
        Args:
            page: Page number
            per_page: Items per page
            is_active: Filter by active status
            
        Returns:
            dict: {packages, total, page, per_page, pages}
        """
        query = DocumentPackage.query
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        query = query.order_by(DocumentPackage.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'packages': [pkg.to_dict(include_documents=True) for pkg in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    
    @staticmethod
    def get_package_by_id(package_id):
        """Get package by ID"""
        return db.session.get(DocumentPackage, package_id)
    
    @staticmethod
    def get_package_by_slug(slug):
        """Get package by slug"""
        return DocumentPackage.query.filter_by(slug=slug, is_active=True).first()
    
    @staticmethod
    def create_package(name, description, price, discount_percent=0, document_ids=None):
        """
        Create a new package
        
        Args:
            name: Package name
            description: Package description
            price: Package price
            discount_percent: Discount percentage
            document_ids: List of document IDs to include
            
        Returns:
            tuple: (package, error_message)
        """
        try:
            package = DocumentPackage(
                name=name,
                description=description,
                price=price,
                discount_percent=discount_percent
            )
            package.generate_slug()
            
            db.session.add(package)
            db.session.flush()  # Get package ID
            
            # Add documents to package
            if document_ids:
                for doc_id in document_ids:
                    document = db.session.get(Document, doc_id)
                    if document:
                        pkg_doc = PackageDocument(
                            package_id=package.id,
                            document_id=doc_id
                        )
                        db.session.add(pkg_doc)
            
            db.session.commit()
            
            return package, None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Failed to create package: {str(e)}'
    
    @staticmethod
    def update_package(package_id, name=None, description=None, price=None, 
                      discount_percent=None, is_active=None):
        """
        Update package
        
        Args:
            package_id: Package ID
            name: New name
            description: New description
            price: New price
            discount_percent: New discount percentage
            is_active: New active status
            
        Returns:
            tuple: (package, error_message)
        """
        try:
            package = db.session.get(DocumentPackage, package_id)
            
            if not package:
                return None, 'Package not found'
            
            # Update fields
            if name is not None:
                package.name = name
                package.generate_slug()
            if description is not None:
                package.description = description
            if price is not None:
                package.price = price
            if discount_percent is not None:
                package.discount_percent = discount_percent
            if is_active is not None:
                package.is_active = is_active
            
            db.session.commit()
            
            return package, None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Failed to update package: {str(e)}'
    
    @staticmethod
    def delete_package(package_id):
        """
        Delete package (soft delete)
        
        Args:
            package_id: Package ID
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            package = db.session.get(DocumentPackage, package_id)
            
            if not package:
                return False, 'Package not found'
            
            # Soft delete
            package.is_active = False
            db.session.commit()
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f'Failed to delete package: {str(e)}'
    
    @staticmethod
    def add_document_to_package(package_id, document_id):
        """
        Add document to package
        
        Args:
            package_id: Package ID
            document_id: Document ID
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            # Verify package and document exist
            package = db.session.get(DocumentPackage, package_id)
            if not package:
                return False, 'Package not found'
            
            document = db.session.get(Document, document_id)
            if not document:
                return False, 'Document not found'
            
            # Check if already exists
            existing = PackageDocument.query.filter_by(
                package_id=package_id,
                document_id=document_id
            ).first()
            
            if existing:
                return False, 'Document already in package'
            
            # Add document
            pkg_doc = PackageDocument(
                package_id=package_id,
                document_id=document_id
            )
            db.session.add(pkg_doc)
            db.session.commit()
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f'Failed to add document to package: {str(e)}'
    
    @staticmethod
    def remove_document_from_package(package_id, document_id):
        """
        Remove document from package
        
        Args:
            package_id: Package ID
            document_id: Document ID
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            pkg_doc = PackageDocument.query.filter_by(
                package_id=package_id,
                document_id=document_id
            ).first()
            
            if not pkg_doc:
                return False, 'Document not in package'
            
            db.session.delete(pkg_doc)
            db.session.commit()
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f'Failed to remove document from package: {str(e)}'
