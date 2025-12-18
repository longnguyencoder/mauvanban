"""
User service for user-related operations
"""
from models import db, SavedDocument, ReportedDocument, User


class UserService:
    """Service for user operations"""
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            tuple: (user, error_message)
        """
        try:
            user = db.session.get(User, user_id)
            if not user:
                return None, 'User not found'
            return user, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def create_user(email, password, full_name=None, phone=None, role='user', is_active=True):
        """
        Create a new user (admin)
        
        Args:
            email: User email
            password: User password
            full_name: User full name
            phone: User phone
            role: User role
            is_active: Active status
            
        Returns:
            tuple: (user, error_message)
        """
        try:
            # Validate email
            from email_validator import validate_email, EmailNotValidError
            try:
                valid = validate_email(email)
                email = valid.email
            except EmailNotValidError as e:
                return None, str(e)
            
            # Check if email already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return None, 'Email already registered'
            
            # Create new user
            user = User(
                email=email,
                full_name=full_name,
                phone_number=phone, # Model uses phone_number, AuthService used phone (check model match)
                role=role,
                is_active=is_active
            )
            # Check if model has phone or phone_number. 
            # In EditUser.tsx it was user.phone_number. 
            # In AuthService it was phone=phone then user = User(phone=phone...).
            # Let's check User model definition to be sure. 
            # But assume phone_number based on previous edits. 
            # Wait, AuthService line 48: phone=phone. 
            # UserService.update_profile line 340: user.phone_number = ...
            # This implies the model might have property alias or inconsistent naming usages.
            # I will check User model first to be safe.
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return user, None
            
        except Exception as e:
            db.session.rollback()
            return None, f'User creation failed: {str(e)}'

    @staticmethod
    def create_user(email, password, full_name=None, phone=None, role='user', is_active=True):
        """
        Create a new user (admin)
        
        Args:
            email: User email
            password: User password
            full_name: User full name
            phone: User phone
            role: User role
            is_active: Active status
            
        Returns:
            tuple: (user, error_message)
        """
        try:
            # Validate email
            from email_validator import validate_email, EmailNotValidError
            try:
                valid = validate_email(email)
                email = valid.email
            except EmailNotValidError as e:
                return None, str(e)
            
            # Check if email already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return None, 'Email already registered'
            
            # Create new user
            user = User(
                email=email,
                full_name=full_name,
                phone=phone,
                role=role,
                is_active=is_active
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return user, None
            
        except Exception as e:
            db.session.rollback()
            return None, f'User creation failed: {str(e)}'

    @staticmethod
    def save_document(user_id, document_id):
        """
        Save/bookmark a document
        
        Args:
            user_id: User ID
            document_id: Document ID
            
        Returns:
            tuple: (saved_document, error_message)
        """
        try:
            # Check if already saved
            existing = SavedDocument.query.filter_by(
                user_id=user_id,
                document_id=document_id
            ).first()
            
            if existing:
                return None, 'Document already saved'
            
            saved_doc = SavedDocument(
                user_id=user_id,
                document_id=document_id
            )
            
            db.session.add(saved_doc)
            db.session.commit()
            
            return saved_doc, None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Failed to save document: {str(e)}'
    
    @staticmethod
    def unsave_document(user_id, document_id):
        """
        Remove saved/bookmarked document
        
        Args:
            user_id: User ID
            document_id: Document ID
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            saved_doc = SavedDocument.query.filter_by(
                user_id=user_id,
                document_id=document_id
            ).first()
            
            if not saved_doc:
                return False, 'Document not saved'
            
            db.session.delete(saved_doc)
            db.session.commit()
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f'Failed to unsave document: {str(e)}'
    
    @staticmethod
    def get_saved_documents(user_id, page=1, per_page=20):
        """
        Get user's saved documents
        
        Args:
            user_id: User ID
            page: Page number
            per_page: Items per page
            
        Returns:
            dict: {documents, total, page, per_page, pages}
        """
        query = SavedDocument.query.filter_by(user_id=user_id).order_by(
            SavedDocument.created_at.desc()
        )
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'documents': [sd.to_dict(include_document=True) for sd in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    
    @staticmethod
    def report_document(user_id, document_id, reason):
        """
        Report a document issue
        
        Args:
            user_id: User ID
            document_id: Document ID
            reason: Report reason
            
        Returns:
            tuple: (report, error_message)
        """
        try:
            if not reason or len(reason.strip()) < 10:
                return None, 'Reason must be at least 10 characters'
            
            report = ReportedDocument(
                user_id=user_id,
                document_id=document_id,
                reason=reason,
                status='pending'
            )
            
            db.session.add(report)
            db.session.commit()
            
            return report, None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Failed to report document: {str(e)}'
    
    @staticmethod
    def get_all_reports(page=1, per_page=20, status=None):
        """
        Get all document reports (admin)
        
        Args:
            page: Page number
            per_page: Items per page
            status: Filter by status
            
        Returns:
            dict: {reports, total, page, per_page, pages}
        """
        query = ReportedDocument.query
        
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(ReportedDocument.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'reports': [report.to_dict(include_details=True) for report in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    
    @staticmethod
    def update_report_status(report_id, status, admin_note=None):
        """
        Update report status (admin)
        
        Args:
            report_id: Report ID
            status: New status
            admin_note: Admin note
            
        Returns:
            tuple: (report, error_message)
        """
        try:
            report = db.session.get(ReportedDocument, report_id)
            
            if not report:
                return None, 'Report not found'
            
            valid_statuses = ['pending', 'reviewing', 'resolved', 'rejected']
            if status not in valid_statuses:
                return None, f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            
            report.status = status
            if admin_note:
                report.admin_note = admin_note
            
            db.session.commit()
            
            return report, None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Failed to update report: {str(e)}'
    
    @staticmethod
    def get_all_users(page=1, per_page=20, role=None, is_active=None):
        """
        Get all users (admin)
        
        Args:
            page: Page number
            per_page: Items per page
            role: Filter by role
            is_active: Filter by active status
            
        Returns:
            dict: {users, total, page, per_page, pages}
        """
        query = User.query
        
        if role:
            query = query.filter_by(role=role)
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        query = query.order_by(User.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'users': [user.to_dict(include_sensitive=True) for user in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    
    @staticmethod
    def toggle_user_active(user_id):
        """
        Toggle user active status (admin)
        
        Args:
            user_id: User ID
            
        Returns:
            tuple: (user, error_message)
        """
        try:
            user = db.session.get(User, user_id)
            
            if not user:
                return None, 'User not found'
            
            user.is_active = not user.is_active
            db.session.commit()
            
            return user, None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Failed to toggle user status: {str(e)}'
    
    @staticmethod
    def adjust_user_balance(user_id, amount, reason=None):
        """
        Adjust user balance (admin)
        
        Args:
            user_id: User ID
            amount: Amount to add (negative to subtract)
            reason: Reason for adjustment
            
        Returns:
            tuple: (user, error_message)
        """
        try:
            user = db.session.get(User, user_id)
            
            if not user:
                return None, 'User not found'
            
            user.balance += amount
            
            if user.balance < 0:
                return None, 'Balance cannot be negative'
            
            db.session.commit()
            
            return user, None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Failed to adjust balance: {str(e)}'
            
    @staticmethod
    def update_user_profile(user_id, **kwargs):
        """
        Update user profile (admin)
        
        Args:
            user_id: User ID
            **kwargs: Fields to update (full_name, email, phone_number, role)
            
        Returns:
            tuple: (user, error_message)
        """
        try:
            user = db.session.get(User, user_id)
            if not user:
                return None, 'User not found'
                
            if 'full_name' in kwargs:
                user.full_name = kwargs['full_name']
                
            if 'email' in kwargs and kwargs['email'] and kwargs['email'] != user.email:
                # Check email duplicate
                existing = User.query.filter_by(email=kwargs['email']).first()
                if existing:
                    return None, 'Email already exists'
                user.email = kwargs['email']
                
            if 'phone_number' in kwargs:
                user.phone = kwargs['phone_number']
                
            if 'role' in kwargs:
                user.role = kwargs['role']
            
            db.session.commit()
            return user, None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Failed to update user: {str(e)}'

    @staticmethod
    def delete_user(user_id):
        """
        Delete user (admin)
        
        Args:
            user_id: User ID
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            user = db.session.get(User, user_id)
            
            if not user:
                return False, 'User not found'
            
            db.session.delete(user)
            db.session.commit()
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f'Failed to delete user: {str(e)}'
