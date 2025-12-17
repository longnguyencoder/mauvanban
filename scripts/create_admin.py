"""
Create admin account script
Run this to create an admin user without needing to seed all data
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import create_app
from models import db
from services import AuthService


def create_admin():
    """Create admin account"""
    
    app = create_app()
    
    with app.app_context():
        print("🔐 Creating admin account...")
        
        # Create tables if not exist
        db.create_all()
        
        # Create admin user
        admin, error = AuthService.create_admin(
            email='admin@mauvanban.vn',
            password='Admin@123',
            full_name='Administrator'
        )
        
        if admin:
            print(f"\n✅ Admin account created successfully!")
            print(f"\n📧 Email:    admin@mauvanban.vn")
            print(f"🔑 Password: Admin@123")
            print(f"\n⚠️  Please change the password after first login!")
        else:
            print(f"\n❌ Error: {error}")
            
            # If admin already exists, show info
            if "already registered" in error.lower():
                print(f"\n💡 Admin account already exists.")
                print(f"📧 Email: admin@mauvanban.vn")
                print(f"\nIf you forgot the password, you can reset it in the database.")


if __name__ == '__main__':
    create_admin()
