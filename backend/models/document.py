"""
Document model for managing templates and forms
"""
import uuid
from datetime import datetime
from slugify import slugify
from . import db


class Document(db.Model):
    """Document model for templates and forms"""
    
    __tablename__ = 'documents'
    
    # Primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Unique identifier
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Basic info
    title = db.Column(db.String(200), nullable=False, index=True)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    
    # Content
    content = db.Column(db.Text)  # Preview content
    file_url = db.Column(db.String(500))  # Actual file location
    file_type = db.Column(db.String(10))  # pdf, docx, xlsx, etc.
    thumbnail_url = db.Column(db.String(500))  # Cover image URL
    
    # Category
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'), nullable=False)
    
    # Pricing
    price = db.Column(db.Numeric(18, 2), default=0, nullable=False)
    
    # Statistics
    views_count = db.Column(db.Integer, default=0, nullable=False)
    downloads_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Features
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # SEO
    meta_keywords = db.Column(db.Text)
    meta_description = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    category = db.relationship('Category', back_populates='documents')
    guide = db.relationship('DocumentGuide', back_populates='document', uselist=False, cascade='all, delete-orphan')
    saved_by_users = db.relationship('SavedDocument', back_populates='document', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', back_populates='document', cascade='all, delete-orphan')
    reports = db.relationship('ReportedDocument', back_populates='document', cascade='all, delete-orphan')
    packages = db.relationship('PackageDocument', back_populates='document', cascade='all, delete-orphan')
    files = db.relationship('DocumentFile', back_populates='document', cascade='all, delete-orphan', order_by='DocumentFile.display_order')
    
    
    def generate_slug(self):
        """Generate URL-friendly slug from title"""
        if not self.slug:
            self.slug = slugify(self.title)
    
    def increment_views(self):
        """Increment view count"""
        self.views_count += 1
    
    def increment_downloads(self):
        """Increment download count"""
        self.downloads_count += 1
    
    def to_dict(self, include_guide=False, include_category=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'code': self.code,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'content': self.content,
            'file_url': self.file_url,
            'thumbnail_url': self.thumbnail_url,
            'file_type': self.file_type,
            'category_id': self.category_id,
            'price': float(self.price),
            'views_count': self.views_count,
            'downloads_count': self.downloads_count,
            'is_featured': self.is_featured,
            'is_active': self.is_active,
            'meta_keywords': self.meta_keywords,
            'meta_description': self.meta_description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_guide and self.guide:
            data['guide'] = self.guide.to_dict()
        
        if include_category and self.category:
            data['category'] = self.category.to_dict()
            
        # Include files if loaded
        if hasattr(self, 'files') and self.files:
            data['files'] = [f.to_dict() for f in self.files]
        
        return data
    
    def __repr__(self):
        return f'<Document {self.code}: {self.title}>'
