
import os
import requests
import hmac
import hashlib
import json
import sys

# Load env from .env file manually if needed, or rely on user having it set
# Ideally, we read .env
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
env_path = os.path.join(parent_dir, '.env')
load_dotenv(env_path)

API_URL = "http://localhost:5000/api/sepay/webhook"
SEPAY_SECRET_KEY = os.getenv('SEPAY_SECRET_KEY')

if not SEPAY_SECRET_KEY:
    print("Error: SEPAY_SECRET_KEY not found in .env")
    sys.exit(1)

def simulate_webhook(transaction_id, amount):
    # Construct transaction code used in payment
    transaction_code = f"MVB{str(transaction_id)[-8:].upper()}"
    
    payload = {
        "id": "SIMULATED_" + transaction_code,
        "gateway": "VCB",
        "transactionDate": "2023-10-27 10:00:00",
        "accountNumber": "1012121212",
        "subAccount": None,
        "transferAmount": amount,
        "transferContent": transaction_code,
        "referenceCode": "REF123",
        "description": "Simulated payment",
        "status": "success"
    }
    
    payload_json = json.dumps(payload)
    
    # Calculate signature
    signature = hmac.new(
        SEPAY_SECRET_KEY.encode('utf-8'),
        payload_json.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        "Content-Type": "application/json",
        "X-Sepay-Signature": signature
    }
    
    print(f"Sending webhook to {API_URL}...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(API_URL, data=payload_json, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ Webhook simulated successfully! The transaction should now be COMPLETED.")
        else:
            print("\n❌ Webhook failed.")
            
    except Exception as e:
        print(f"Error sending request: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/simulate_sepay_webhook.py <transaction_id> <amount>")
        print("Example: python scripts/simulate_sepay_webhook.py 550e8400-e29b-41d4-a716-446655440000 50000")
        sys.exit(1)
        
    transaction_id = sys.argv[1]
    amount = int(sys.argv[2])
    
    simulate_webhook(transaction_id, amount)
