"""
Database models package
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

# Import models for Alembic to detect
from .user import User
from .category import Category
from .document import Document
from .document_guide import DocumentGuide
from .document_file import DocumentFile
from .document_package import DocumentPackage
from .package_document import PackageDocument
from .saved_document import SavedDocument
from .transaction import Transaction
from .reported_document import ReportedDocument
from .news import News

__all__ = [
    'db',
    'migrate',
    'mail',
    'User',
    'Category',
    'Document',
    'DocumentGuide',
    'DocumentFile',
    'DocumentPackage',
    'PackageDocument',
    'SavedDocument',
    'Transaction',
    'ReportedDocument',
    'News'
]
