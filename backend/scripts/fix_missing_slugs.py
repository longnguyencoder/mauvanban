"""
Script to fix missing slugs for existing documents
"""
import os
import sys
from slugify import slugify

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import create_app
from models import db, Document

def fix_slugs():
    app = create_app()
    with app.app_context():
        print("🔍 Checking for documents with missing slugs...")
        
        # Find documents with null or empty slug
        # Note: In some DBs, if it was nullable=False but no default, it might be empty string or NULL
        documents = Document.query.filter((Document.slug == None) | (Document.slug == '')).all()
        
        if not documents:
            print("✅ No documents found with missing slugs.")
            
            # Additional check: verify if slugs are unique and look valid
            print("🔍 Verifying existing slugs...")
            all_docs = Document.query.all()
            for doc in all_docs:
                if not doc.slug or len(doc.slug) < 2:
                    documents.append(doc)
            
            if not documents:
                print("✅ All existing slugs look valid.")
                return

        print(f"🛠️ Found {len(documents)} documents to fix.")
        
        for doc in documents:
            try:
                base_slug = slugify(doc.title) if doc.title else f"document-{doc.id[:8]}"
                slug = base_slug
                counter = 1
                
                # Ensure uniqueness
                while Document.query.filter(Document.slug == slug, Document.id != doc.id).first():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                
                doc.slug = slug
                print(f"   ✓ Fixed: '{doc.title}' -> {slug}")
                
            except Exception as e:
                print(f"   ❌ Error fixing document {doc.id}: {e}")
        
        try:
            db.session.commit()
            print("✅ Successfully updated all slugs.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error committing changes: {e}")

if __name__ == "__main__":
    fix_slugs()
