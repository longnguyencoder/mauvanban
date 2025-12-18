from main import create_app
from models import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print(f"Connected to DB: {app.config['SQLALCHEMY_DATABASE_URI']}")
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS thumbnail_url VARCHAR(500)"))
            conn.commit()
            print("Successfully added thumbnail_url column (PostgreSQL).")
    except Exception as e:
        print(f"Migration Error: {e}")
