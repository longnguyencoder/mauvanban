import os
import requests
import json
import hmac
import hashlib
from app import app, db
from models import Transaction
import argparse

def simulate_sepay_webhook(transaction_id):
    """
    Simulate a SePay webhook call for a specific transaction.
    """
    with app.app_context():
        # 1. Fetch Transaction
        transaction = db.session.get(Transaction, transaction_id)
        if not transaction:
            print(f"Error: Transaction with ID {transaction_id} not found.")
            return

        print(f"Found Transaction: {transaction.id} | Amount: {transaction.amount} | Status: {transaction.payment_status}")

        if transaction.payment_status == 'completed':
            print("Transaction is already completed.")
            # We can still send the webhook, but the backend might say "Already processed".

        # 2. Get Config
        secret_key = os.getenv('SEPAY_SECRET_KEY')
        if not secret_key:
            print("Error: SEPAY_SECRET_KEY not found in environment.")
            return

        # 3. Construct Payload
        # Format: DH{last 8 chars of ID}
        short_id = str(transaction.id)[-8:].upper()
        transaction_code = f"DH{short_id}"

        payload_data = {
            "id": f"SIM_{transaction.id}", # Simulated bank transaction ID
            "gateway": "ACB",
            "transactionDate": "2024-12-18 10:00:00",
            "accountNumber": "LOCSPAY000324416",
            "subAccount": None,
            "transferAmount": int(transaction.amount),
            "transferContent": transaction_code,
            "referenceCode": "REF123",
            "description": f"Payment for {transaction_code}",
            "status": "success"
        }
        
        payload_json = json.dumps(payload_data)

        # 4. Generate Signature
        signature = hmac.new(
            secret_key.encode('utf-8'),
            payload_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # 5. Send Request
        webhook_url = "http://localhost:5000/api/sepay/webhook"
        headers = {
            "Content-Type": "application/json",
            "X-Sepay-Signature": signature
        }

        print(f"\nSending Webhook to {webhook_url}...")
        print(f"Payload: {payload_json}")
        print(f"Signature: {signature}")

        try:
            response = requests.post(webhook_url, headers=headers, data=payload_json)
            print(f"\nResponse Code: {response.status_code}")
            print(f"Response Body: {response.text}")
        except Exception as e:
            print(f"\nError sending request: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simulate SePay Webhook')
    parser.add_argument('transaction_id', nargs='?', help='The ID of the transaction to simulate payment for')
    args = parser.parse_args()

    if args.transaction_id:
        simulate_sepay_webhook(args.transaction_id)
    else:
        # Interactive mode: List pending transactions
        with app.app_context():
            pending_txs = Transaction.query.filter_by(payment_status='pending').order_by(Transaction.created_at.desc()).limit(10).all()
            
            if not pending_txs:
                print("No pending transactions found.")
                exit()
            
            print("\nRecent Pending Transactions:")
            print(f"{'ID':<38} | {'Amount':<10} | {'Created At'}")
            print("-" * 70)
            for i, tx in enumerate(pending_txs):
                print(f"{i+1}. {tx.id:<36} | {tx.amount:,.0f} | {tx.created_at}")
            
            try:
                choice = int(input("\nSelect transaction # to pay (or 0 to exit): "))
                if 1 <= choice <= len(pending_txs):
                    selected_tx = pending_txs[choice-1]
                    simulate_sepay_webhook(selected_tx.id)
                else:
                    print("Exiting.")
            except ValueError:
                print("Invalid input.")
