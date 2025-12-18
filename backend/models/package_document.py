"""
Package-Document association model
"""
from . import db


class PackageDocument(db.Model):
    """Many-to-many relationship between packages and documents"""
    
    __tablename__ = 'package_documents'
    
    # Composite primary key
    package_id = db.Column(db.String(36), db.ForeignKey('document_packages.id'), primary_key=True)
    document_id = db.Column(db.String(36), db.ForeignKey('documents.id'), primary_key=True)
    
    # Relationships
    package = db.relationship('DocumentPackage', back_populates='documents')
    document = db.relationship('Document', back_populates='packages')
    
    def __repr__(self):
        return f'<PackageDocument package={self.package_id} document={self.document_id}>'
