"""
Transaction service for payments and purchases
"""
from decimal import Decimal
from datetime import datetime
from models import db, Transaction, User, Document, DocumentPackage
from .sepay_service import SepayService


class TransactionService:
    """Service for transaction operations"""
    
    @staticmethod
    def purchase_document(user_id, document_id):
        """
        Purchase a document using user balance
        
        Args:
            user_id: User ID
            document_id: Document ID
            
        Returns:
            tuple: (transaction, error_message)
        """
        try:
            user = db.session.get(User, user_id)
            if not user:
                return None, 'User not found'
            
            document = db.session.get(Document, document_id)
            if not document:
                return None, 'Document not found'
            
            # Check if already purchased
            existing = Transaction.query.filter_by(
                user_id=user_id,
                document_id=document_id,
                transaction_type='document',
                status='completed'
            ).first()
            
            if existing:
                return None, 'Document already purchased'
            
            # Check balance
            if user.balance < document.price:
                return None, 'Insufficient balance'
            
            # Create transaction
            transaction = Transaction(
                user_id=user_id,
                transaction_type='document',
                document_id=document_id,
                amount=document.price,
                status='pending',
                payment_method='balance'
            )
            
            # Deduct balance
            user.balance -= document.price
            
            # Mark as completed
            transaction.status = 'completed'
            
            db.session.add(transaction)
            db.session.commit()
            
            return transaction, None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Purchase failed: {str(e)}'
    
    @staticmethod
    def purchase_package(user_id, package_id):
        """
        Purchase a package using user balance
        
        Args:
            user_id: User ID
            package_id: Package ID
            
        Returns:
            tuple: (transaction, error_message)
        """
        try:
            user = db.session.get(User, user_id)
            if not user:
                return None, 'User not found'
            
            package = db.session.get(DocumentPackage, package_id)
            if not package:
                return None, 'Package not found'
            
            # Check if already purchased
            existing = Transaction.query.filter_by(
                user_id=user_id,
                package_id=package_id,
                transaction_type='package',
                status='completed'
            ).first()
            
            if existing:
                return None, 'Package already purchased'
            
            # Check balance
            if user.balance < package.price:
                return None, 'Insufficient balance'
            
            # Create transaction
            transaction = Transaction(
                user_id=user_id,
                transaction_type='package',
                package_id=package_id,
                amount=package.price,
                status='pending',
                payment_method='balance'
            )
            
            # Deduct balance
            user.balance -= package.price
            
            # Mark as completed
            transaction.status = 'completed'
            
            db.session.add(transaction)
            db.session.commit()
            
            return transaction, None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Purchase failed: {str(e)}'
    
            db.session.add(transaction)
            db.session.commit()
            
            return transaction, None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Purchase failed: {str(e)}'
    
    @staticmethod
    def create_sepay_payment(user_id, item_type, item_id):
        """
        Create a SePay payment request for an item
        
        Args:
            user_id: User ID
            item_type: 'document' or 'package'
            item_id: Item ID
            
        Returns:
            tuple: (payment_info, error_message)
        """
        try:
            # Get user
            user = db.session.get(User, user_id)
            if not user:
                return None, 'User not found'
            
            # Get item and amount
            amount = 0
            document_id = None
            package_id = None
            description = ""
            
            if item_type == 'document':
                item = db.session.get(Document, item_id)
                if not item:
                    return None, 'Document not found'
                
                # Check directly purchased
                if TransactionService.check_user_purchased_document(user_id, item_id):
                    return None, 'Document already purchased'
                    
                amount = item.price
                document_id = item.id
                description = f"Thanh toan tai lieu {item.code}"
                
            elif item_type == 'package':
                item = db.session.get(DocumentPackage, item_id)
                if not item:
                    return None, 'Package not found'
                
                # Check already purchased
                existing = Transaction.query.filter_by(
                    user_id=user_id,
                    package_id=item_id,
                    transaction_type='package',
                    status='completed'
                ).first()
                if existing:
                    return None, 'Package already purchased'
                    
                amount = item.price
                package_id = item.id
                description = f"Thanh toan goi {item.name}"
            else:
                return None, 'Invalid item type'
            
            # Check for existing pending transaction
            pending_query = Transaction.query.filter_by(
                user_id=user_id,
                transaction_type=item_type,
                status='pending',
                payment_method='sepay',
                payment_status='pending'
            )
            
            if item_type == 'document':
                pending_query = pending_query.filter_by(document_id=document_id)
            else:
                pending_query = pending_query.filter_by(package_id=package_id)
                
            transaction = pending_query.first()
            
            # Create new transaction if not exists or create a new request for existing one
            if not transaction:
                transaction = Transaction(
                    user_id=user_id,
                    transaction_type=item_type,
                    document_id=document_id,
                    package_id=package_id,
                    amount=amount,
                    status='pending',
                    payment_method='sepay',
                    payment_status='pending'
                )
                db.session.add(transaction)
                db.session.commit()
            
            # Create SePay payment request
            payment_info, error = SepayService.create_payment_request(
                transaction.id, 
                amount,
                description
            )
            
            if error:
                return None, error
            
            # Update transaction with QR code info
            transaction.qr_code_url = payment_info['qr_code']
            transaction.expires_at = datetime.fromisoformat(payment_info['expires_at'])
            transaction.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return payment_info, None
            
        except Exception as e:
            db.session.rollback()
            return None, f"Failed to create SePay payment: {str(e)}"
        """
        Top up user balance
        
        Args:
            user_id: User ID
            amount: Amount to add
            payment_method: Payment method
            payment_info: Additional payment information
            
        Returns:
            tuple: (transaction, error_message)
        """
        try:
            user = db.session.get(User, user_id)
            if not user:
                return None, 'User not found'
            
            if amount <= 0:
                return None, 'Invalid amount'
            
            # Create transaction
            transaction = Transaction(
                user_id=user_id,
                transaction_type='topup',
                amount=amount,
                status='completed',  # In real app, this would be pending until payment confirmed
                payment_method=payment_method,
                payment_info=payment_info
            )
            
            # Add to balance
            user.balance += Decimal(str(amount))
            
            db.session.add(transaction)
            db.session.commit()
            
            return transaction, None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Top-up failed: {str(e)}'
    
    @staticmethod
    def check_user_purchased_document(user_id, document_id):
        """
        Check if user has purchased a document
        
        Args:
            user_id: User ID
            document_id: Document ID
            
        Returns:
            bool: True if purchased
        """
        # Check direct purchase
        direct_purchase = Transaction.query.filter_by(
            user_id=user_id,
            document_id=document_id,
            transaction_type='document',
            status='completed'
        ).first()
        
        if direct_purchase:
            return True
        
        # Check if purchased via package
        package_purchases = Transaction.query.filter_by(
            user_id=user_id,
            transaction_type='package',
            status='completed'
        ).all()
        
        for purchase in package_purchases:
            if purchase.package:
                for pkg_doc in purchase.package.documents:
                    if pkg_doc.document_id == document_id:
                        return True
        
        return False
    
    @staticmethod
    def get_user_transactions(user_id, page=1, per_page=20, transaction_type=None):
        """
        Get user transaction history
        
        Args:
            user_id: User ID
            page: Page number
            per_page: Items per page
            transaction_type: Filter by type
            
        Returns:
            dict: {transactions, total, page, per_page, pages}
        """
        query = Transaction.query.filter_by(user_id=user_id)
        
        if transaction_type:
            query = query.filter_by(transaction_type=transaction_type)
        
        query = query.order_by(Transaction.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'transactions': [txn.to_dict(include_details=True) for txn in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    
    @staticmethod
    def get_purchased_documents(user_id):
        """
        Get all documents purchased by user
        
        Args:
            user_id: User ID
            
        Returns:
            list: List of documents
        """
        documents = []
        
        # Direct purchases
        direct_purchases = Transaction.query.filter_by(
            user_id=user_id,
            transaction_type='document',
            status='completed'
        ).all()
        
        for purchase in direct_purchases:
            if purchase.document:
                documents.append(purchase.document)
        
        # Package purchases
        package_purchases = Transaction.query.filter_by(
            user_id=user_id,
            transaction_type='package',
            status='completed'
        ).all()
        
        for purchase in package_purchases:
            if purchase.package:
                for pkg_doc in purchase.package.documents:
                    if pkg_doc.document and pkg_doc.document not in documents:
                        documents.append(pkg_doc.document)
        
        return documents
