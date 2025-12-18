
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import create_app
from models import db, User
from werkzeug.security import generate_password_hash

def reset_admin():
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email='admin@mauvanban.vn').first()
        if user:
            print(f"Found user {user.email}. Resetting password to 'admin123'")
            user.password_hash = generate_password_hash('admin123')
            db.session.commit()
            print("Password reset successful.")
        else:
            print("User admin@mauvanban.vn not found. Creating...")
            from services import AuthService
            AuthService.create_admin('admin@mauvanban.vn', 'admin123', 'Super Admin')
            print("Admin created.")

if __name__ == "__main__":
    reset_admin()
