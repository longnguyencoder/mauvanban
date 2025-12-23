
import os
import json
import sys
import hmac
import hashlib
from urllib import request, parse

def load_env_manually(env_path):
    """Đọc file .env mà không cần thư viện bên ngoài"""
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"').strip("'")
    return env_vars

# Tìm file .env
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
env_path = os.path.join(parent_dir, '.env')

# Load cấu hình
config = load_env_manually(env_path)

# CONFIGURATION
API_URL = config.get('WEBHOOK_TEST_URL', "http://localhost:5000/api/sepay/webhook")
SEPAY_SECRET_KEY = config.get('SEPAY_SECRET_KEY')
SEPAY_VIRTUAL_ACCOUNT = config.get('SEPAY_VIRTUAL_ACCOUNT', '')
SEPAY_BANK_NAME = config.get('SEPAY_BANK_NAME', 'ACB')
SEPAY_BANK_ACCOUNT = config.get('SEPAY_BANK_ACCOUNT', '9924666')

if not SEPAY_SECRET_KEY:
    print("Error: SEPAY_SECRET_KEY không tìm thấy trong file .env")
    sys.exit(1)

def simulate_webhook(transaction_id_suffix, amount):
    # 1. Tạo nội dung chuyển khoản
    transaction_code = f"DH{transaction_id_suffix.upper()}"
    
    if SEPAY_VIRTUAL_ACCOUNT:
        full_content = f"{SEPAY_VIRTUAL_ACCOUNT} {transaction_code}"
    else:
        full_content = transaction_code
        
    payload = {
        "id": f"SIM_{transaction_id_suffix}_{os.urandom(2).hex()}",
        "gateway": SEPAY_BANK_NAME,
        "transactionDate": "2024-01-01 10:00:00",
        "accountNumber": SEPAY_BANK_ACCOUNT,
        "transferAmount": amount,
        "transferContent": full_content,
        "content": full_content,
        "transferType": "in",
        "status": "success"
    }
    
    payload_json = json.dumps(payload).encode('utf-8')
    
    # 2. Tạo Header xác thực
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"<policy {SEPAY_SECRET_KEY}>",
        "User-Agent": "SePay-Simulated-Client/2.0"
    }
    
    print(f"--- GIẢ LẬP WEBHOOK SEPAY (STANDALONE) ---")
    print(f"Target URL: {API_URL}")
    print(f"Virtual Account: {SEPAY_VIRTUAL_ACCOUNT}")
    print(f"Full Content: {full_content}")
    print(f"Amount: {amount:,} VND")
    print("-" * 40)
    
    try:
        req = request.Request(API_URL, data=payload_json, headers=headers, method='POST')
        with request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            body = response.read().decode('utf-8')
            
            print(f"Status Code: {status}")
            print(f"Response: {body}")
            
            if status == 200:
                print("\n✅ Webhook gửi THÀNH CÔNG!")
            else:
                print(f"\n❌ Webhook trả về lỗi {status}")
                
    except Exception as e:
        print(f"\n❌ Lỗi kết nối: {e}")
        print("Gợi ý: Nếu chạy trên VPS, hãy đảm bảo URL là https://mauvanban.vn/api/sepay/webhook")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Cách dùng: python3 scripts/simulate_sepay_webhook.py <8_số_cuối_ID> <số_tiền>")
        print("Ví dụ: python3 scripts/simulate_sepay_webhook.py F242FF41 56000")
        sys.exit(1)
        
    tx_id = sys.argv[1]
    amt = int(sys.argv[2])
    
    simulate_webhook(tx_id, amt)
