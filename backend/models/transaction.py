"""
Transaction model for payments and purchases
"""
import uuid
from datetime import datetime
from . import db


class Transaction(db.Model):
    """Transaction model for tracking purchases and payments"""
    
    __tablename__ = 'transactions'
    
    # Primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Transaction type
    transaction_type = db.Column(db.String(20), nullable=False)  # 'document', 'package', 'topup'
    
    # Related items (nullable based on type)
    document_id = db.Column(db.String(36), db.ForeignKey('documents.id'), nullable=True)
    package_id = db.Column(db.String(36), db.ForeignKey('document_packages.id'), nullable=True)
    
    # Amount
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Status
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, completed, failed, refunded
    
    # Payment details
    payment_method = db.Column(db.String(50))  # balance, vnpay, momo, sepay, etc.
    payment_info = db.Column(db.JSON)  # Additional payment information
    
    # SePay specific fields
    payment_status = db.Column(db.String(50), default='pending')  # pending, completed, failed, cancelled
    sepay_transaction_id = db.Column(db.String(255))  # Transaction ID from SePay
    sepay_data = db.Column(db.JSON)  # Raw webhook data from SePay
    qr_code_url = db.Column(db.Text)  # QR code data URL (base64)
    expires_at = db.Column(db.DateTime)  # Payment expiration time
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', back_populates='transactions')
    document = db.relationship('Document', back_populates='transactions')
    package = db.relationship('DocumentPackage', back_populates='transactions')
    
    def to_dict(self, include_details=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'transaction_type': self.transaction_type,
            'document_id': self.document_id,
            'package_id': self.package_id,
            'amount': float(self.amount),
            'status': self.status,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'qr_code_url': self.qr_code_url,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_details:
            if self.document:
                data['document'] = self.document.to_dict()
            if self.package:
                data['package'] = self.package.to_dict()
            if self.payment_info:
                data['payment_info'] = self.payment_info
        
        return data
    
    def __repr__(self):
        return f'<Transaction {self.id}: {self.transaction_type} - {self.status}>'
