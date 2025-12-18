import sqlite3
import os

# Absolute path based on workspace
db_path = r'c:/Users/PT COMPUTER/Documents/GitHub/mauvanban/instance/mauvanban.sqlite'

if __name__ == "__main__":
    print(f"Connecting to {db_path}...")
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        exit(1)
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Checking if thumbnail_url column exists...")
        cursor.execute("PRAGMA table_info(documents)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'thumbnail_url' in columns:
            print("Column thumbnail_url already exists.")
        else:
            print("Adding thumbnail_url column...")
            cursor.execute("ALTER TABLE documents ADD COLUMN thumbnail_url VARCHAR(500)")
            conn.commit()
            print("Success!")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
