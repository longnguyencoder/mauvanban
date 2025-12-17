"""
Reported Document model for user reports
"""
import uuid
from datetime import datetime
from . import db


class ReportedDocument(db.Model):
    """User reports about document issues"""
    
    __tablename__ = 'reported_documents'
    
    # Primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    document_id = db.Column(db.String(36), db.ForeignKey('documents.id'), nullable=False)
    
    # Report details
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, reviewing, resolved, rejected
    admin_note = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', back_populates='reports')
    document = db.relationship('Document', back_populates='reports')
    
    def to_dict(self, include_details=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'document_id': self.document_id,
            'reason': self.reason,
            'status': self.status,
            'admin_note': self.admin_note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_details:
            if self.user:
                data['user'] = self.user.to_dict()
            if self.document:
                data['document'] = self.document.to_dict()
        
        return data
    
    def __repr__(self):
        return f'<ReportedDocument {self.id}: {self.status}>'
