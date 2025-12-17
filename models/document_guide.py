"""
Document Guide model for usage instructions
"""
import uuid
from datetime import datetime
from . import db


class DocumentGuide(db.Model):
    """Guide and instructions for using documents"""
    
    __tablename__ = 'document_guides'
    
    # Primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key
    document_id = db.Column(db.String(36), db.ForeignKey('documents.id'), unique=True, nullable=False)
    
    # Guide sections
    usage_guide = db.Column(db.Text)  # Hướng dẫn sử dụng
    filling_guide = db.Column(db.Text)  # Hướng dẫn điền
    submission_guide = db.Column(db.Text)  # Hướng dẫn nộp
    required_documents = db.Column(db.Text)  # Hồ sơ cần thiết
    fees_info = db.Column(db.Text)  # Thông tin lệ phí
    notes = db.Column(db.Text)  # Ghi chú
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    document = db.relationship('Document', back_populates='guide')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'usage_guide': self.usage_guide,
            'filling_guide': self.filling_guide,
            'submission_guide': self.submission_guide,
            'required_documents': self.required_documents,
            'fees_info': self.fees_info,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<DocumentGuide for document {self.document_id}>'
