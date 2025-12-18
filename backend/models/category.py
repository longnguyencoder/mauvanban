"""
Category model with hierarchical structure
"""
import uuid
from datetime import datetime
from slugify import slugify
from . import db


class Category(db.Model):
    """Category model for organizing documents"""
    
    __tablename__ = 'categories'
    
    # Primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic info
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    
    # Hierarchy support
    parent_id = db.Column(db.String(36), db.ForeignKey('categories.id'), nullable=True)
    
    # Display
    icon = db.Column(db.String(100))  # Icon class or URL
    display_order = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    children = db.relationship('Category', 
                              backref=db.backref('parent', remote_side=[id]),
                              cascade='all, delete-orphan')
    documents = db.relationship('Document', back_populates='category', cascade='all, delete-orphan')
    
    # generate_slug moved to service for better uniqueness control

    
    def to_dict(self, include_children=False, include_documents=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'parent_id': self.parent_id,
            'icon': self.icon,
            'display_order': self.display_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_children:
            data['children'] = [child.to_dict() for child in self.children if child.is_active]
        
        if include_documents:
            data['documents_count'] = len([doc for doc in self.documents if doc.is_active])
        
        return data
    
    def __repr__(self):
        return f'<Category {self.name}>'
