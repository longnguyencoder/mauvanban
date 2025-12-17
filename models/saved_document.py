"""
Saved Document model for user bookmarks
"""
import uuid
from datetime import datetime
from . import db


class SavedDocument(db.Model):
    """User's saved/bookmarked documents"""
    
    __tablename__ = 'saved_documents'
    
    # Primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    document_id = db.Column(db.String(36), db.ForeignKey('documents.id'), nullable=False)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'document_id', name='unique_user_document'),
    )
    
    # Relationships
    user = db.relationship('User', back_populates='saved_documents')
    document = db.relationship('Document', back_populates='saved_by_users')
    
    def to_dict(self, include_document=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'document_id': self.document_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_document and self.document:
            data['document'] = self.document.to_dict(include_category=True)
        
        return data
    
    def __repr__(self):
        return f'<SavedDocument user={self.user_id} document={self.document_id}>'
