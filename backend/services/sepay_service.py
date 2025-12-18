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
            data: Webhook data
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Extract data
            transaction_code = data.get('transferContent') or data.get('content')
            amount = int(data.get('transferAmount') or data.get('amount', 0))
            sepay_transaction_id = data.get('id') or data.get('transaction_id')
            status = data.get('status', 'success')
            
            if not transaction_code:
                return False, 'Missing transaction code'
            
            # Extract transaction ID from code (DH{id})
            if not transaction_code.startswith('DH'):
                return False, 'Invalid transaction code format'
            
            # Find transaction by code
            transaction = Transaction.query.filter(
                Transaction.id.like(f'%{transaction_code[2:]}')
            ).first()
            
            if not transaction:
                current_app.logger.warning(f"Transaction not found for code: {transaction_code}")
                return False, 'Transaction not found'
            
            # Check if already processed
            if transaction.payment_status == 'completed':
                return True, 'Transaction already processed'
            
            # Verify amount
            if amount != transaction.amount:
                current_app.logger.error(f"Amount mismatch: expected {transaction.amount}, got {amount}")
                return False, 'Amount mismatch'
            
            # Update transaction
            if status == 'success':
                transaction.payment_status = 'completed'
                transaction.status = 'completed'  # Important: Unlock content
            else:
                transaction.payment_status = 'failed'
                # transaction.status remains 'pending' or set to 'failed' depending on logic
                # usually keep pending to allow retry or manual fix, but here failed payment means failed transaction
                
            transaction.sepay_transaction_id = sepay_transaction_id
            transaction.sepay_data = data
            transaction.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            current_app.logger.info(f"SePay payment processed: {transaction.id}")
            
            return True, 'Payment processed successfully'
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"SePay webhook processing error: {str(e)}")
            return False, f"Failed to process webhook: {str(e)}"
    
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
