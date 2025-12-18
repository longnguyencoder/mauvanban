import psycopg2
from urllib.parse import urlparse

def test_connection(password):
    try:
        # Construct DSN
        dsn = f"postgresql://postgres:{password}@localhost:5432/mauvanban_db"
        conn = psycopg2.connect(dsn)
        conn.close()
        return True
    except Exception as e:
        return False

def find_password():
    common_passwords = [
        'postgres',
        '123456',
        '12345678',
        'password',
        'admin',
        'root',
        '1234',
        '1',
        ''  # Empty password
    ]

    print("🔍 Attempting to find correct PostgreSQL password...")
    
    for pwd in common_passwords:
        display_pwd = pwd if pwd else "(empty string)"
        print(f"   Trying password: '{display_pwd}'...", end=" ")
        
        if test_connection(pwd):
            print("✅ SUCCESS!")
            print("\n🎉 FOUND IT! Your correct database password is:")
            print(f"👉 {pwd if pwd else '(empty string)'}")
            print(f"\nPlease update your .env file to:")
            if pwd:
                print(f"DATABASE_URL=postgresql://postgres:{pwd}@localhost:5432/mauvanban_db")
            else:
                print(f"DATABASE_URL=postgresql://postgres@localhost:5432/mauvanban_db")
            return
        else:
            print("❌ Failed")

    print("\n😞 Could not find the password in common list.")
    print("Please try to recall your PostgreSQL password or reset it using pgAdmin.")

if __name__ == "__main__":
    find_password()
