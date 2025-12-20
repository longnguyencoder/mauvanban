"""
Diagnostic script to check for common document data issues
"""
import os
import sys
from sqlalchemy import text

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import create_app
from models import db, Document, Category, DocumentFile, DocumentGuide

def diagnose():
    app = create_app()
    with app.app_context():
        print("🔍 Starting data diagnostics...")
        
        # 1. Check for documents with missing slugs
        print("\n1. Checking for missing slugs...")
        missing_slugs = Document.query.filter((Document.slug == None) | (Document.slug == '')).count()
        if missing_slugs > 0:
            print(f"   ❌ Found {missing_slugs} documents with missing slugs!")
        else:
            print("   ✅ All documents have slugs.")
            
        # 2. Check for NULL values in non-nullable columns
        print("\n2. Checking for NULL values in critical columns...")
        critical_fields = ['price', 'views_count', 'downloads_count', 'is_active', 'is_featured']
        for field in critical_fields:
            try:
                count = Document.query.filter(getattr(Document, field) == None).count()
                if count > 0:
                    print(f"   ❌ Found {count} documents with NULL {field}!")
                else:
                    print(f"   ✅ Column {field} is clean.")
            except Exception as e:
                print(f"   ⚠️  Could not check {field}: {e}")

        # 3. Check for documents without categories
        print("\n3. Checking for documents without categories...")
        no_cat = Document.query.filter(Document.category_id == None).count()
        if no_cat > 0:
            print(f"   ❌ Found {no_cat} documents without category_id!")
        else:
            print("   ✅ All documents have category_id.")

        # 4. Check for broken category relationships
        print("\n4. Checking for broken category relationships...")
        all_docs = Document.query.all()
        broken_cats = 0
        for doc in all_docs:
            if doc.category_id and not doc.category:
                broken_cats += 1
        if broken_cats > 0:
            print(f"   ❌ Found {broken_cats} documents with invalid category_id (category not found)!")
        else:
            print("   ✅ Category relationships are intact.")

        # 5. Check for table existence and columns
        print("\n5. Checking table structure...")
        tables = {
            'documents': ['id', 'title', 'slug', 'price', 'views_count', 'downloads_count', 'is_featured', 'is_active', 'file_type', 'thumbnail_url'],
            'categories': ['id', 'name', 'slug'],
            'transactions': ['id', 'user_id', 'transaction_type', 'status', 'amount', 'payment_status', 'sepay_transaction_id', 'qr_code_url', 'expires_at'],
            'document_files': ['id', 'document_id', 'file_url', 'preview_url'],
            'document_guides': ['id', 'document_id', 'usage_guide']
        }
        
        with db.engine.connect() as conn:
            for table, columns in tables.items():
                try:
                    # Check table
                    conn.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
                    print(f"   ✅ Table '{table}' exists.")
                    
                    # Check columns
                    for col in columns:
                        try:
                            conn.execute(text(f"SELECT {col} FROM {table} LIMIT 1"))
                        except Exception:
                            print(f"      ❌ Column '{col}' is MISSING in table '{table}'!")
                except Exception as e:
                    print(f"   ❌ Table '{table}' might be missing or inaccessible.")

        print("\n🏁 Diagnostics completed.")
        print("\n💡 Tip: If columns are missing in 'transactions', run: python scripts/add_sepay_fields.py")
        print("💡 Tip: If columns are missing in 'documents', run: python scripts/add_missing_columns.py")
        print("💡 To see detailed server error, run: sudo journalctl -u mauvanban-backend -f")

if __name__ == "__main__":
    diagnose()
