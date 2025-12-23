
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Mock Flask app context if needed
from flask import Flask
app = Flask(__name__)

with app.app_context():
    from services.sepay_service import SepayService
    
    print("=== SePay Configuration Check ===")
    config = SepayService._get_config()
    for k, v in config.items():
        if 'key' in k or 'secret' in k:
            print(f"{k}: {v[:5]}...{v[-5:]}" if v else f"{k}: None")
        else:
            print(f"{k}: {v}")
            
    print("\n=== Transaction Code Generation Check ===")
    tx_id = "test-uuid-12345678"
    code = SepayService.generate_transaction_code(tx_id)
    print(f"Transaction ID: {tx_id}")
    print(f"Generated Code: {code}")
    
    print("\n=== Webhook Auth Check ===")
    auth_header = f"<policy {os.getenv('SEPAY_SECRET_KEY')}>"
    is_valid = SepayService.verify_webhook_api_key(auth_header)
    print(f"Auth Header: {auth_header}")
    print(f"Is Valid: {is_valid}")
    
    print("\n=== QR URL Check ===")
    payment_info, error = SepayService.create_payment_request(tx_id, 50000)
    if error:
        print(f"Error: {error}")
    else:
        print(f"QR URL: {payment_info['qr_code']}")
        print(f"Content: {payment_info['content']}")
