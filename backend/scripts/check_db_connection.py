
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add parent directory to path to find .env if run from scripts dir
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env explicitly
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

def check_connection():
    db_url = os.getenv('DATABASE_URL')
    print("--- Database Connection Check ---")
    
    if not db_url:
        print("ERROR: DATABASE_URL not found in .env")
        return

    # Mask password for display
    safe_url = db_url
    if "@" in db_url:
        try:
            part1 = db_url.split("@")[0]
            part2 = db_url.split("@")[1]
            if ":" in part1:
                prefix = part1.split(":")[0] 
                # user:***@host...
                safe_url = f"{prefix}:***@{part2}"
        except:
            pass
            
    print(f"Attempting to connect to: {safe_url}")
    
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("SUCCESS! Database connection established.")
            print(f"Test Query Result: {result.fetchone()}")
    except Exception as e:
        print("\nCONNECTION FAILED!")
        print(f"Error details: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check if PostgreSQL service is running: sudo systemctl status postgresql")
        print("2. Check if username/password are correct.")
        print("3. Check if database name exists.")
        print("4. If password has '@', make sure it is encoded as '%40'.")

if __name__ == "__main__":
    check_connection()
