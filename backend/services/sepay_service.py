"""
SePay Payment Service
Handles SePay bank transfer payment integration
"""
import os
import hmac
import hashlib
import requests
import qrcode
import io
import base64
from datetime import datetime, timedelta
from models import db, Transaction
from flask import current_app


class SepayService:
    """Service for SePay payment operations"""
    
    @staticmethod
    def _get_config():
        """Get SePay configuration from environment"""
        return {
            'api_key': os.getenv('SEPAY_API_KEY'),
            'account_id': os.getenv('SEPAY_ACCOUNT_ID'),
            'secret_key': os.getenv('SEPAY_SECRET_KEY'),
            'bank_account': os.getenv('SEPAY_BANK_ACCOUNT'),
            'bank_name': os.getenv('SEPAY_BANK_NAME', 'VCB'),
            'account_name': os.getenv('SEPAY_ACCOUNT_NAME'),
            'enabled': os.getenv('SEPAY_ENABLED', 'True') == 'True',
            'timeout': int(os.getenv('SEPAY_TIMEOUT', '900'))  # 15 minutes
        }
    
    @staticmethod
    def is_enabled():
        """Check if SePay is enabled"""
        config = SepayService._get_config()
        return config['enabled'] and config['api_key']
    
    @staticmethod
    def generate_transaction_code(transaction_id):
        """
        Generate unique transaction code for bank transfer content
        Format: MVB{transaction_id_last_8_chars}
        """
        # Get last 8 characters of transaction ID
        short_id = str(transaction_id)[-8:].upper()
        return f"MVB{short_id}"
    
    @staticmethod
    def create_payment_request(transaction_id, amount, description="Thanh toan van ban"):
        """
        Create SePay payment request and generate QR code
        
        Args:
            transaction_id: Transaction ID
            amount: Payment amount
            description: Payment description
            
        Returns:
            dict: Payment info with QR code
        """
        try:
            config = SepayService._get_config()
            
            if not config['enabled']:
                return None, 'SePay payment is not enabled'
            
            # Generate transaction code (DH + last 8 chars)
            # Example: DH1A2B3C
            short_id = str(transaction_id)[-8:].upper()
            transaction_code = f"DH{short_id}"
            
            # Create payment info
            payment_info = {
                'bank_account': config['bank_account'],
                'bank_name': config['bank_name'],
                'account_name': config['account_name'] or 'MAU VAN BAN', 
                'amount': int(amount),
                'content': transaction_code,
                'transaction_id': str(transaction_id),
                'expires_at': (datetime.utcnow() + timedelta(seconds=config['timeout'])).isoformat() + 'Z'
            }
            
            # Generate SePay QR URL
            # https://qr.sepay.vn/img?acc=...
            acc = config['bank_account']
            bank = config['bank_name']
            des = transaction_code
            
            qr_url = f"https://qr.sepay.vn/img?acc={acc}&bank={bank}&amount={int(amount)}&des={des}"
            
            payment_info['qr_code'] = qr_url
            
            return payment_info, None
            
        except Exception as e:
            current_app.logger.error(f"SePay create payment error: {str(e)}")
            return None, f"Failed to create payment: {str(e)}"
    
    @staticmethod
    def verify_webhook_signature(payload, signature):
        """
        Verify webhook signature from SePay
        
        Args:
            payload: Request payload (string)
            signature: Signature from header
            
        Returns:
            bool: True if valid
        """
        try:
            config = SepayService._get_config()
            secret_key = config['secret_key']
            
            # Calculate expected signature
            expected_signature = hmac.new(
                secret_key.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception as e:
            current_app.logger.error(f"SePay signature verification error: {str(e)}")
            return False
    
    @staticmethod
    def process_payment_webhook(data):
        """
        Process payment webhook from SePay
        
        Args:
            data: Webhook data dict
            
        Returns:
            tuple: (success, message)
        """
        try:
            # 1. Extract data - support both CamelCase (SePay Docs) and snake_case
            # Mapping based on SePay Webhook documentation
            gateway = data.get('gateway')
            account_number = data.get('accountNumber') or data.get('account_number')
            transfer_type = data.get('transferType') or data.get('transfer_type', 'in')
            transfer_amount = float(data.get('transferAmount') or data.get('amount') or 0)
            accumulated = float(data.get('accumulated') or 0)
            
            # Content is the most important field for matching
            transaction_content = data.get('content') or data.get('transferContent') or ""
            reference_code = data.get('referenceCode') or data.get('reference_number')
            sepay_transaction_id = str(data.get('id') or data.get('transaction_id') or "")
            
            current_app.logger.info(f"Processing SePay webhook: ID={sepay_transaction_id}, Content='{transaction_content}', Amount={transfer_amount}")

            if not transaction_content:
                return False, 'Missing transaction content'
            
            if transfer_type != 'in' and transfer_type != 'IN':
                return True, 'Not a credit transaction, skipping'

            # 2. Match transaction by content (looking for DHXXXXXXXX)
            # We use a case-insensitive search to be safe
            import re
            match = re.search(r'DH([A-Z0-9]{8})', transaction_content.upper())
            
            if not match:
                current_app.logger.warning(f"No order code (DH...) found in content: {transaction_content}")
                return False, 'No order code found in content'
            
            order_code_suffix = match.group(1)
            
            # Find transaction in DB
            # We match by the last 8 characters of the UUID which we used to generate the code
            transaction = Transaction.query.filter(
                Transaction.id.ilike(f'%{order_code_suffix}')
            ).first()
            
            if not transaction:
                current_app.logger.warning(f"No transaction found in database for code suffix: {order_code_suffix}")
                return False, f'Transaction not found for code suffix {order_code_suffix}'
            
            # 3. Validation
            if transaction.payment_status == 'completed':
                return True, 'Transaction already processed'
            
            # Allow a small difference (e.g. transfer fees if any) but usually it should match
            if abs(transfer_amount - float(transaction.amount)) > 10: 
                current_app.logger.error(f"Amount mismatch for {transaction.id}: Expected {transaction.amount}, got {transfer_amount}")
                return False, f'Amount mismatch: expected {transaction.amount}, got {transfer_amount}'
            
            # 4. Success - Update transaction and related entities
            transaction.payment_status = 'completed'
            transaction.status = 'completed'
            transaction.sepay_transaction_id = sepay_transaction_id
            transaction.sepay_data = data # Store full payload for audit
            transaction.updated_at = datetime.utcnow()
            
            # If it's a top-up, we might need to update balance here if not handled elsewhere
            # But usually TransactionService handles 'topup' type status changes.
            if transaction.transaction_type == 'topup':
                user = transaction.user
                if user:
                    from decimal import Decimal
                    user.balance += Decimal(str(transfer_amount))
                    current_app.logger.info(f"Top-up completed for user {user.id}, new balance: {user.balance}")

            db.session.commit()
            current_app.logger.info(f"Successfully processed SePay payment for transaction {transaction.id}")
            
            return True, 'Payment processed successfully'
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"SePay webhook processing error: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return False, f"Internal error processing webhook: {str(e)}"
    
    @staticmethod
    def check_transaction_status(transaction_id):
        """
        Double-check transaction status with SePay API
        If local status is pending, query SePay API to see if payment arrived.
        """
        try:
            config = SepayService._get_config()
            
            transaction = db.session.get(Transaction, transaction_id)
            
            if not transaction:
                return None, 'Transaction not found'

            # If already completed, return immediately
            if transaction.payment_status == 'completed':
                 return {
                    'transaction_id': str(transaction.id),
                    'payment_status': transaction.payment_status,
                    'amount': int(transaction.amount),
                    'sepay_transaction_id': transaction.sepay_transaction_id
                }, None

            # If pending and SePay is enabled, check with SePay API
            if config['enabled'] and config['api_key']:
                try:
                    # Generate the content code we expect (e.g. MVB12345)
                    expected_content = SepayService.generate_transaction_code(transaction.id)
                    # Note: In create_payment_request we used DH + id. Let's match that.
                    # The generate_transaction_code method uses MVB, but create_payment_request uses DH.
                    # Let's fix create_payment_request consistency later, but for now match what was generated.
                    short_id = str(transaction.id)[-8:].upper()
                    expected_content = f"DH{short_id}" 

                    # Call SePay API
                    # API Doc: https://sepay.vn/api
                    url = "https://my.sepay.vn/userapi/transactions/list"
                    headers = {
                        "Authorization": f"Bearer {config['api_key']}",
                        "Content-Type": "application/json"
                    }
                    
                    # Filter param (optional optimization)
                    # We can fetch last 20 transactions
                    params = {
                        "limit": 20,
                    }

                    response = requests.get(url, headers=headers, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('status') == 200:
                            transactions = data.get('messages', {}).get('transactions', [])
                            
                            for tx in transactions:
                                # Check if content matches
                                tx_content = tx.get('transaction_content', '')
                                tx_amount = float(tx.get('amount_in', 0))
                                
                                # Use simple inclusion check as bank content often has extra text
                                if expected_content in tx_content:
                                    # Verify amount
                                    if abs(tx_amount - float(transaction.amount)) < 1000: # Allow small diff or exact match
                                        # MATCH FOUND!
                                        current_app.logger.info(f"SePay API: Found match for {transaction.id}")
                                        
                                        transaction.payment_status = 'completed'
                                        transaction.status = 'completed' 
                                        transaction.sepay_transaction_id = str(tx.get('id'))
                                        transaction.sepay_data = tx
                                        transaction.updated_at = datetime.utcnow()
                                        
                                        db.session.commit()
                                        break
                except Exception as api_error:
                    current_app.logger.warning(f"Failed to query SePay API: {str(api_error)}")
            
            return {
                'transaction_id': str(transaction.id),
                'payment_status': transaction.payment_status,
                'amount': int(transaction.amount),
                'sepay_transaction_id': transaction.sepay_transaction_id
            }, None
            
        except Exception as e:
            current_app.logger.error(f"SePay status check error: {str(e)}")
            return None, f"Failed to check status: {str(e)}"
    
    @staticmethod
    def cancel_payment(transaction_id):
        """
        Cancel pending payment
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            tuple: (success, message)
        """
        try:
            transaction = db.session.get(Transaction, transaction_id)
            
            if not transaction:
                return False, 'Transaction not found'
            
            if transaction.payment_status == 'completed':
                return False, 'Cannot cancel completed transaction'
            
            transaction.payment_status = 'cancelled'
            transaction.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return True, 'Payment cancelled successfully'
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"SePay cancel payment error: {str(e)}")
            return False, f"Failed to cancel payment: {str(e)}"
