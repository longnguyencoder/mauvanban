
import os

env_path = 'backend/.env'
if os.path.exists(env_path):
    with open(env_path, 'rb') as f:
        content = f.read()
    
    # Remove null bytes and other common encoding issues
    clean_content = content.replace(b'\x00', b'')
    
    # Write back as clean UTF-8
    with open(env_path, 'wb') as f:
        f.write(clean_content)
    print(f"Cleaned {env_path}")
else:
    print(f"{env_path} not found")
