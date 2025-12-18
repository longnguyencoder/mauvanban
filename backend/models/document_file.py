"""
Document File model for storing multiple files attached to a document
"""
import uuid
from datetime import datetime
from . import db

class DocumentFile(db.Model):
    """Document File model"""
    
    __tablename__ = 'document_files'
    
    # Primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key
    document_id = db.Column(db.String(36), db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    
    # File info
    file_url = db.Column(db.String(500), nullable=False)
    preview_url = db.Column(db.String(500))  # URL of the generated preview image (blurred page 1)
    file_type = db.Column(db.String(10))  # pdf, doc, docx, etc.
    original_filename = db.Column(db.String(255))
    file_size = db.Column(db.Integer)  # Size in bytes
    
    # Order
    display_order = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document = db.relationship('Document', back_populates='files')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'file_url': self.file_url,
            'preview_url': self.preview_url,
            'file_type': self.file_type,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'display_order': self.display_order,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<DocumentFile {self.original_filename}>'
