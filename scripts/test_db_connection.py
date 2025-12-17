"""
Test database connection
Run this to verify database connection is working
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from config import config


def test_connection():
    """Test database connection"""
    
    print("🔍 Testing database connection...\n")
    
    # Get database URL from config
    cfg = config['development']
    db_url = cfg.SQLALCHEMY_DATABASE_URI
    
    print(f"📍 Database URL: {db_url}")
    print(f"   (hiding password for security)\n")
    
    try:
        # Try to connect
        print("⏳ Attempting to connect...")
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Test query
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            
            print("✅ Connection successful!\n")
            print(f"📊 PostgreSQL version:")
            print(f"   {version}\n")
            
            # Check if database exists
            result = conn.execute(text("SELECT current_database();"))
            current_db = result.fetchone()[0]
            print(f"📁 Current database: {current_db}\n")
            
            # List tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            
            if tables:
                print(f"📋 Existing tables ({len(tables)}):")
                for table in tables:
                    print(f"   - {table[0]}")
                print()
            else:
                print("📋 No tables found yet (database is empty)")
                print("   Run migrations to create tables:\n")
                print("   flask db init")
                print("   flask db migrate -m 'Initial migration'")
                print("   flask db upgrade\n")
            
            return True
            
    except Exception as e:
        print("❌ Connection failed!\n")
        print(f"Error: {str(e)}\n")
        
        if "does not exist" in str(e):
            print("💡 Database does not exist. Create it with:")
            print("   createdb mauvanban_db")
            print("\n   Or in psql:")
            print("   CREATE DATABASE mauvanban_db;\n")
        elif "password authentication failed" in str(e):
            print("💡 Check your database credentials in .env file")
            print("   Make sure DATABASE_URL is correct\n")
        elif "could not connect to server" in str(e):
            print("💡 PostgreSQL server is not running")
            print("   Start PostgreSQL service first\n")
        
        return False


if __name__ == '__main__':
    success = test_connection()
    
    if success:
        print("🎉 Database is ready!")
        print("\n📝 Next steps:")
        print("   1. Run migrations: flask db upgrade")
        print("   2. Create admin: python scripts/create_admin.py")
        print("   3. Start server: python main.py")
    else:
        print("⚠️  Please fix the connection issue first")
