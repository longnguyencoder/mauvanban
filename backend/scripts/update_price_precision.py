
import os
import sys
from sqlalchemy import text

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import create_app
from models import db

def update_price_precision():
    app = create_app()
    with app.app_context():
        print(f"Connected to DB: {app.config['SQLALCHEMY_DATABASE_URI']}")
        try:
            with db.engine.connect() as conn:
                # For PostgreSQL: ALTER TABLE documents ALTER COLUMN price TYPE NUMERIC(18, 2)
                # Note: This syntax works for PostgreSQL.
                conn.execute(text("ALTER TABLE documents ALTER COLUMN price TYPE NUMERIC(18, 2)"))
                conn.commit()
                print("Successfully updated price column precision to NUMERIC(18, 2)")
        except Exception as e:
            print(f"Error: {e}")
            # Fallback for SQLite just in case (though unlikely given the error)
            # SQLite doesn't strictly enforce numeric precision usually, but if it was the issue, 
            # we'd need a different approach (create new table, copy, drop).
            # Assuming PostgreSQL for now.

if __name__ == "__main__":
    update_price_precision()
