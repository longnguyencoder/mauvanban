"""
SePay Payment Service - FIXED VERSION
Handles SePay bank transfer payment integration
"""
import os
import hmac
import hashlib
import requests
import re
from datetime import datetime, timedelta
from decimal import Decimal
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
            'virtual_account': os.getenv('SEPAY_VIRTUAL_ACCOUNT', ''),  # FIXED: Added
            'enabled': os.getenv('SEPAY_ENABLED', 'True') == 'True',
            'timeout': int(os.getenv('SEPAY_TIMEOUT', '900')),
            'api_url': os.getenv('SEPAY_API_URL', 'https://my.sepay.vn/companyapi')  # FIXED: Default to companyapi
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
        
        FIXED: Support virtual account
        Format without VA: DH{last_8_chars}
        Format with VA: LOCSPAY000324416 DH{last_8_chars}
        """
        config = SepayService._get_config()
        virtual_account = config.get('virtual_account', '')
        
        # Get last 8 characters of transaction ID
        short_id = str(transaction_id)[-8:].upper()
        transaction_code = f"DH{short_id}"
        
        # Add virtual account prefix if configured
        if virtual_account:
            return f"{virtual_account} {transaction_code}"
        
        return transaction_code
    
    @staticmethod
    def create_payment_request(transaction_id, amount, description="Thanh toan van ban"):
        """
        Create SePay payment request and generate QR code
        
        FIXED: Use consistent transaction code generation
        """
        try:
            config = SepayService._get_config()
            
            if not config['enabled']:
                return None, 'SePay payment is not enabled'
            
            # FIXED: Use generate_transaction_code method
            transaction_code = SepayService.generate_transaction_code(transaction_id)
            
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
            acc = config['bank_account']
            bank = config['bank_name']
            # FIXED: URL encode transaction code (especially for space in virtual account)
            from urllib.parse import quote
            des = quote(transaction_code)
            
            qr_url = f"https://qr.sepay.vn/img?acc={acc}&bank={bank}&amount={int(amount)}&des={des}"
            
            payment_info['qr_code'] = qr_url
            
            current_app.logger.info(f"Created payment: {transaction_id} -> {transaction_code}")
            
            return payment_info, None
            
        except Exception as e:
            current_app.logger.error(f"SePay create payment error: {str(e)}")
            return None, f"Failed to create payment: {str(e)}"
    
    @staticmethod
    def verify_webhook_api_key(api_key):
        """
        FIXED: Verify API key from webhook header
        
        Your SePay config uses API Key authentication, NOT signature
        Header format: authorization: <policy mauvanban_secret_2024>
        """
        try:
            config = SepayService._get_config()
            expected_key = config['secret_key']
            
            if not expected_key:
                current_app.logger.warning("SEPAY_SECRET_KEY not configured in .env")
                return False
            
            if not api_key:
                current_app.logger.warning("No API key provided in webhook")
                return False
            
            # FIXED: Robust key cleaning
            # 1. Strip expected key to remove any \r or spaces from .env
            expected_key = expected_key.strip()
            
            # 2. Extract key from header (remove <policy...>, Apikey, Bearer, etc.)
            # We take the last word in the header to be safe
            clean_key = api_key.strip()
            if ' ' in clean_key:
                clean_key = clean_key.split(' ')[-1]
            
            # Remove any trailing > if using <policy ...>
            clean_key = clean_key.replace('>', '').strip()
            
            # Secure comparison
            is_valid = hmac.compare_digest(clean_key, expected_key)
            
            if not is_valid:
                current_app.logger.warning(
                    f"SePay Auth Mismatch: Received '{clean_key}', Expected '{expected_key}'"
                )
            
            return is_valid
            
        except Exception as e:
            current_app.logger.error(f"API key verification error: {str(e)}")
            return False
    
    @staticmethod
    def verify_webhook_signature(payload, signature):
        """
        DEPRECATED: Keep for backward compatibility
        Use verify_webhook_api_key instead
        """
        return SepayService.verify_webhook_api_key(signature)
    
    @staticmethod
    def process_payment_webhook(data):
        """
        FIXED: Process payment webhook from SePay with proper validation
        """
        try:
            # Extract sepay_transaction_id early for idempotency check
            sepay_transaction_id = str(
                data.get('id') or 
                data.get('transaction_id') or 
                ''
            )
            
            if not sepay_transaction_id:
                return False, 'Missing SePay transaction ID'
            
            # FIXED: IDEMPOTENCY CHECK - Has this webhook been processed?
            existing = Transaction.query.filter_by(
                sepay_transaction_id=sepay_transaction_id
            ).first()
            
            if existing:
                current_app.logger.info(
                    f"Webhook already processed: SePay ID {sepay_transaction_id}"
                )
                return True, 'Webhook already processed (idempotent)'
            
            # Extract webhook data with multiple fallbacks
            transfer_type = (
                data.get('transferType') or 
                data.get('transfer_type') or 
                'in'
            ).lower()
            
            transfer_amount = float(
                data.get('transferAmount') or 
                data.get('transfer_amount') or
                data.get('amount_in') or 
                data.get('amount') or 
                0
            )
            
            transaction_content = (
                data.get('content') or 
                data.get('transaction_content') or
                data.get('transferContent') or 
                ''
            )
            
            current_app.logger.info(
                f"Processing webhook: SePay ID={sepay_transaction_id}, "
                f"Content='{transaction_content}', Amount={transfer_amount}"
            )
            
            # Validate transfer type
            if transfer_type not in ['in', 'credit']:
                return True, 'Not an incoming transfer, skipping'
            
            if not transaction_content:
                return False, 'Missing transaction content'
            
            # FIXED: Extract transaction code (support both with and without virtual account)
            # Pattern 1: LOCSPAY000324416 DH12345678
            # Pattern 2: DH12345678
            match = re.search(r'DH([A-Z0-9]{8})', transaction_content.upper())
            
            if not match:
                current_app.logger.warning(
                    f"No order code (DH...) found in content: '{transaction_content}'"
                )
                return False, f'No order code found in content: {transaction_content}'
            
            order_code_suffix = match.group(1)
            current_app.logger.info(f"Extracted order code suffix: {order_code_suffix}")
            
            # Find transaction in DB
            transaction = Transaction.query.filter(
                Transaction.id.ilike(f'%{order_code_suffix}')
            ).first()
            
            if not transaction:
                current_app.logger.warning(
                    f"No transaction found for code suffix: {order_code_suffix}"
                )
                return False, f'Transaction not found for code suffix {order_code_suffix}'
            
            current_app.logger.info(f"Found transaction: {transaction.id}")
            
            # Validate transaction state
            if transaction.payment_status == 'completed':
                current_app.logger.info(f"Transaction {transaction.id} already completed")
                return True, 'Transaction already completed'
            
            # Validate amount (allow small tolerance)
            expected_amount = float(transaction.amount)
            amount_diff = abs(transfer_amount - expected_amount)
            
            if amount_diff > 1000:  # 1000 VND tolerance
                current_app.logger.error(
                    f"Amount mismatch for {transaction.id}: "
                    f"Expected {expected_amount}, got {transfer_amount}, "
                    f"difference {amount_diff}"
                )
                return False, f'Amount mismatch: expected {expected_amount}, got {transfer_amount}'
            
            # SUCCESS - Update transaction
            transaction.payment_status = 'completed'
            transaction.status = 'completed'
            transaction.sepay_transaction_id = sepay_transaction_id
            transaction.sepay_data = data
            transaction.updated_at = datetime.utcnow()
            
            # Handle top-up transactions
            if transaction.transaction_type == 'topup' and transaction.user:
                user = transaction.user
                old_balance = user.balance
                user.balance += Decimal(str(transfer_amount))
                current_app.logger.info(
                    f"Top-up for user {user.id}: {old_balance} -> {user.balance}"
                )
            
            db.session.commit()
            
            current_app.logger.info(
                f"✅ Successfully processed payment for transaction {transaction.id}"
            )
            
            return True, 'Payment processed successfully'
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Webhook processing error: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return False, f"Internal error: {str(e)}"
    
    @staticmethod
    def check_transaction_status(transaction_id):
        """
        FIXED: Check transaction status with correct API URL
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

            # If pending, check with SePay API
            if config['enabled'] and config['api_key']:
                try:
                    # FIXED: Use generate_transaction_code method
                    expected_content = SepayService.generate_transaction_code(transaction.id)
                    
                    # FIXED: Use correct API URL from config
                    api_url = config.get('api_url', 'https://my.sepay.vn/companyapi')
                    url = f"{api_url}/transactions/list"
                    
                    headers = {
                        "Authorization": f"Bearer {config['api_key']}",
                        "Content-Type": "application/json"
                    }
                    
                    current_app.logger.info(f"Calling SePay API: {url}")
                    
                    response = requests.get(url, headers=headers, params={"limit": 50}, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # FIXED: Support both userapi and companyapi response formats
                        if data.get('status') == 200:
                            # userapi format
                            transactions = data.get('messages', {}).get('transactions', [])
                        elif data.get('status') == 'success':
                            # companyapi format
                            transactions = data.get('data', {}).get('transactions', [])
                        else:
                            transactions = []
                        
                        for tx in transactions:
                            tx_content = tx.get('transaction_content', '')
                            tx_amount = float(tx.get('amount_in', 0))
                            
                            # Check if content matches (case-insensitive)
                            if expected_content.upper() in tx_content.upper():
                                # Verify amount
                                if abs(tx_amount - float(transaction.amount)) < 1000:
                                    # MATCH FOUND!
                                    current_app.logger.info(f"SePay API: Found match for {transaction.id}")
                                    
                                    transaction.payment_status = 'completed'
                                    transaction.status = 'completed' 
                                    transaction.sepay_transaction_id = str(tx.get('id'))
                                    transaction.sepay_data = tx
                                    transaction.updated_at = datetime.utcnow()
                                    
                                    if transaction.transaction_type == 'topup' and transaction.user:
                                        transaction.user.balance += Decimal(str(tx_amount))
                                    
                                    db.session.commit()
                                    break
                    else:
                        current_app.logger.warning(f"SePay API error: {response.status_code}")
                        
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
        """Cancel pending payment"""
        try:
            transaction = db.session.get(Transaction, transaction_id)
            
            if not transaction:
                return False, 'Transaction not found'
            
            if transaction.payment_status == 'completed':
                return False, 'Cannot cancel completed transaction'
            
            transaction.payment_status = 'cancelled'
            transaction.status = 'cancelled'
            transaction.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return True, 'Payment cancelled successfully'
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"SePay cancel payment error: {str(e)}")
            return False, f"Failed to cancel payment: {str(e)}"
