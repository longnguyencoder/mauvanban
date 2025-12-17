"""
Document Package model for bundling documents
"""
import uuid
from datetime import datetime
from slugify import slugify
from . import db


class DocumentPackage(db.Model):
    """Package model for bundling multiple documents"""
    
    __tablename__ = 'document_packages'
    
    # Primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic info
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    
    # Pricing
    price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_percent = db.Column(db.Numeric(5, 2), default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    documents = db.relationship('PackageDocument', back_populates='package', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', back_populates='package', cascade='all, delete-orphan')
    
    def generate_slug(self):
        """Generate URL-friendly slug from name"""
        if not self.slug:
            self.slug = slugify(self.name)
    
    def calculate_original_price(self):
        """Calculate total price of all documents in package"""
        total = sum(pd.document.price for pd in self.documents if pd.document)
        return float(total)
    
    def calculate_savings(self):
        """Calculate savings amount"""
        original = self.calculate_original_price()
        return original - float(self.price)
    
    def to_dict(self, include_documents=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'price': float(self.price),
            'discount_percent': float(self.discount_percent),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_documents:
            data['documents'] = [pd.document.to_dict() for pd in self.documents if pd.document]
            data['documents_count'] = len(self.documents)
            data['original_price'] = self.calculate_original_price()
            data['savings'] = self.calculate_savings()
        
        return data
    
    def __repr__(self):
        return f'<DocumentPackage {self.name}>'
