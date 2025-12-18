
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import create_app
from models import db

def update_schema():
    app = create_app()
    with app.app_context():
        print("Creating missing tables...")
        db.create_all()
        print("Schema update completed.")

if __name__ == "__main__":
    update_schema()
