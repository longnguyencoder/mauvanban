"""
Database migration: Add SePay fields to transactions table
"""
import sys
import os

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db
from sqlalchemy import text


def upgrade():
    """Add SePay fields to transactions table"""
    print("Adding SePay fields to transactions table...")
    
    with db.engine.connect() as conn:
        # Add payment_status column
        conn.execute(text("""
            ALTER TABLE transactions 
            ADD COLUMN IF NOT EXISTS payment_status VARCHAR(50) DEFAULT 'pending'
        """))
        
        # Add sepay_transaction_id column
        conn.execute(text("""
            ALTER TABLE transactions 
            ADD COLUMN IF NOT EXISTS sepay_transaction_id VARCHAR(255)
        """))
        
        # Add sepay_data column
        conn.execute(text("""
            ALTER TABLE transactions 
            ADD COLUMN IF NOT EXISTS sepay_data JSON
        """))
        
        # Add qr_code_url column
        conn.execute(text("""
            ALTER TABLE transactions 
            ADD COLUMN IF NOT EXISTS qr_code_url TEXT
        """))
        
        # Add expires_at column
        conn.execute(text("""
            ALTER TABLE transactions 
            ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP
        """))
        
        # Create indexes for better query performance
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_transactions_sepay_transaction_id 
            ON transactions(sepay_transaction_id)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_transactions_payment_status 
            ON transactions(payment_status)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_transactions_expires_at 
            ON transactions(expires_at)
        """))
        
        conn.commit()
    
    print("✅ SePay fields added successfully!")


def downgrade():
    """Remove SePay fields from transactions table"""
    print("Removing SePay fields from transactions table...")
    
    with db.engine.connect() as conn:
        # Drop indexes
        conn.execute(text("DROP INDEX IF EXISTS idx_transactions_sepay_transaction_id"))
        conn.execute(text("DROP INDEX IF EXISTS idx_transactions_payment_status"))
        conn.execute(text("DROP INDEX IF EXISTS idx_transactions_expires_at"))
        
        # Drop columns
        conn.execute(text("ALTER TABLE transactions DROP COLUMN IF EXISTS payment_status"))
        conn.execute(text("ALTER TABLE transactions DROP COLUMN IF EXISTS sepay_transaction_id"))
        conn.execute(text("ALTER TABLE transactions DROP COLUMN IF EXISTS sepay_data"))
        conn.execute(text("ALTER TABLE transactions DROP COLUMN IF EXISTS qr_code_url"))
        conn.execute(text("ALTER TABLE transactions DROP COLUMN IF EXISTS expires_at"))
        
        conn.commit()
    
    print("✅ SePay fields removed successfully!")


if __name__ == '__main__':
    from main import create_app
    import os
    
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    
    with app.app_context():
        print("Running SePay migration...")
        upgrade()
        print("Migration completed!")
