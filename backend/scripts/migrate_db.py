import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import create_app
from extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print(f"Connected to: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    try:
        with db.engine.connect() as conn:
            # Postgres supports IF NOT EXISTS for ADD COLUMN since 9.6
            conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS thumbnail_url VARCHAR(500)"))
            conn.commit()
            print("Successfully added thumbnail_url column to documents table (PostgreSQL).")
            
    except Exception as e:
        print(f"Error during migration: {str(e)}")
