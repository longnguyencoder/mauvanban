
import os
import sys
from sqlalchemy import text

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import create_app
from models import db

def add_columns():
    app = create_app()
    with app.app_context():
        print("Checking for missing columns in 'documents' table...")
        
        # Columns to add if missing
        columns = [
            ("views_count", "INTEGER DEFAULT 0 NOT NULL"),
            ("downloads_count", "INTEGER DEFAULT 0 NOT NULL"),
            ("is_featured", "BOOLEAN DEFAULT FALSE NOT NULL"),
            ("is_active", "BOOLEAN DEFAULT TRUE NOT NULL"),
            ("file_type", "VARCHAR(10)"),
            ("thumbnail_url", "VARCHAR(500)"),
            ("meta_keywords", "TEXT"),
            ("meta_description", "TEXT")
        ]
        
        with db.engine.connect() as conn:
            # Get existing columns
            # Note: This is a simplified check. For robust check we could inspect schema.
            # But simple ALTER TABLE ... ADD COLUMN IF NOT EXISTS is PostgreSQL specific (Postgres 9.6+).
            # Assuming Postgres.
            
            for col_name, col_type in columns:
                try:
                    print(f"Attempting to add column {col_name}...")
                    conn.execute(text(f"ALTER TABLE documents ADD COLUMN IF NOT EXISTS {col_name} {col_type};"))
                    conn.commit()
                    print(f"Checked/Added {col_name}")
                except Exception as e:
                    print(f"Error checking {col_name}: {e}")
                    # Try to see if it failed because it exists (for older Postgres versions)
                    pass

        print("Column check completed.")

if __name__ == "__main__":
    add_columns()
