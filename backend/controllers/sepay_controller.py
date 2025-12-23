"""
SePay Payment Controller - FIXED VERSION
Handles webhook callbacks and payment status checks
"""
from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from services.sepay_service import SepayService
from services.transaction_service import TransactionService
from middleware import token_required
import json

# Create namespace
sepay_ns = Namespace('sepay', description='SePay payment operations')


@sepay_ns.route('/create')
class SepayCreate(Resource):
    """Create SePay payment"""
    
    @token_required
    @sepay_ns.doc(description='Create SePay payment request', security='Bearer')
    @sepay_ns.expect(sepay_ns.model('SepayCreate', {
        'item_type': fields.String(required=True, description='Type of item (document/package)'),
        'item_id': fields.String(required=True, description='ID of the item')
    }))
    def post(self, current_user):
        """Create payment"""
        try:
            data = request.get_json()
            item_type = data.get('item_type')
            item_id = data.get('item_id')
            
            if not item_type or not item_id:
                return {
                    'success': False,
                    'message': 'Missing item_type or item_id'
                }, 400
            
            payment_info, error = TransactionService.create_sepay_payment(
                current_user.id, item_type, item_id
            )
            
            if error:
                return {
                    'success': False,
                    'message': error
                }, 400
            
            return {
                'success': True,
                'data': payment_info
            }, 200
            
        except Exception as e:
            current_app.logger.error(f"SePay create error: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return {
                'success': False,
                'message': 'Failed to create payment'
            }, 500


@sepay_ns.route('/webhook')
class SepayWebhook(Resource):
    """
    FIXED: SePay webhook endpoint with proper authentication
    """
    
    @sepay_ns.doc(description='Receive webhook from SePay')
    def post(self):
        """Process SePay webhook"""
        try:
            # Log all headers for debugging
            headers_dict = dict(request.headers)
            current_app.logger.info("=== SePay Webhook Received ===")
            current_app.logger.info(f"Headers: {json.dumps(headers_dict, indent=2)}")
            
            # Get raw payload
            payload = request.get_data(as_text=True)
            current_app.logger.info(f"Raw Payload: {payload}")
            
            # FIXED: Get authorization header (support both cases)
            auth_header = (
                request.headers.get('authorization') or  # lowercase
                request.headers.get('Authorization') or  # uppercase
                ''
            )
            
            current_app.logger.info(f"Auth header: {auth_header[:50]}...")
            
            # Parse JSON data
            try:
                data = json.loads(payload)
            except json.JSONDecodeError as e:
                current_app.logger.error(f"Invalid JSON: {str(e)}")
                return {
                    'success': False,
                    'message': 'Invalid JSON payload'
                }, 400
            
            # FIXED: Verify API key (not signature!)
            if not SepayService.verify_webhook_api_key(auth_header):
                current_app.logger.error("Invalid webhook authentication")
                return {
                    'success': False,
                    'message': 'Invalid authentication'
                }, 401
            
            # Process webhook
            success, message = SepayService.process_payment_webhook(data)
            
            current_app.logger.info(f"Processing result: {success}, {message}")
            
            if success:
                return {
                    'success': True,
                    'message': message
                }, 200
            else:
                # Return 200 to prevent SePay retry for known errors
                return {
                    'success': False,
                    'message': message
                }, 200
                
        except Exception as e:
            current_app.logger.error(f"SePay webhook error: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            
            # Return 500 to trigger SePay retry
            return {
                'success': False,
                'message': 'Internal server error'
            }, 500


@sepay_ns.route('/check/<string:transaction_id>')
class SepayCheck(Resource):
    """Check SePay transaction status"""
    
    @token_required
    @sepay_ns.doc(description='Check SePay transaction status', security='Bearer')
    def get(self, current_user, transaction_id):
        """Check transaction status"""
        try:
            # FIXED: Add authorization check
            from models import Transaction
            transaction = Transaction.query.get(transaction_id)
            
            if not transaction:
                return {
                    'success': False,
                    'message': 'Transaction not found'
                }, 404
            
            # Check if transaction belongs to current user
            if transaction.user_id != current_user.id:
                return {
                    'success': False,
                    'message': 'Unauthorized'
                }, 403
            
            result, error = SepayService.check_transaction_status(transaction_id)
            
            if error:
                return {
                    'success': False,
                    'message': error
                }, 400
            
            return {
                'success': True,
                'data': result
            }, 200
            
        except Exception as e:
            current_app.logger.error(f"SePay check error: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return {
                'success': False,
                'message': 'Failed to check status'
            }, 500


@sepay_ns.route('/cancel/<string:transaction_id>')
class SepayCancel(Resource):
    """Cancel SePay payment"""
    
    @token_required
    @sepay_ns.doc(description='Cancel pending SePay payment', security='Bearer')
    def post(self, current_user, transaction_id):
        """Cancel payment"""
        try:
            # FIXED: Add authorization check
            from models import Transaction
            transaction = Transaction.query.get(transaction_id)
            
            if not transaction:
                return {
                    'success': False,
                    'message': 'Transaction not found'
                }, 404
            
            # Check if transaction belongs to current user
            if transaction.user_id != current_user.id:
                return {
                    'success': False,
                    'message': 'Unauthorized'
                }, 403
            
            success, message = SepayService.cancel_payment(transaction_id)
            
            if success:
                return {
                    'success': True,
                    'message': message
                }, 200
            else:
                return {
                    'success': False,
                    'message': message
                }, 400
                
        except Exception as e:
            current_app.logger.error(f"SePay cancel error: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return {
                'success': False,
                'message': 'Failed to cancel payment'
            }, 500


@sepay_ns.route('/test')
class SepayTest(Resource):
    """
    NEW: Test webhook endpoint (development only)
    """
    
    @sepay_ns.doc(description='Test SePay webhook (dev only)')
    def post(self):
        """Test webhook with sample data"""
        # Only allow in development
        if not current_app.config.get('DEBUG'):
            return {
                'success': False,
                'message': 'Only available in debug mode'
            }, 403
        
        try:
            data = request.get_json() or {}
            
            # Create test webhook data
            test_data = {
                'id': data.get('id', 'test_12345'),
                'gateway': data.get('gateway', 'ACB'),
                'transaction_content': data.get('content', 'LOCSPAY000324416 DH12345678'),
                'content': data.get('content', 'LOCSPAY000324416 DH12345678'),
                'transferAmount': data.get('amount', 50000),
                'amount_in': data.get('amount', 50000),
                'transferType': 'in',
                'transfer_type': 'in',
                **data
            }
            
            current_app.logger.info(f"Test webhook data: {json.dumps(test_data, indent=2)}")
            
            success, message = SepayService.process_payment_webhook(test_data)
            
            return {
                'success': success,
                'message': message,
                'test_data': test_data
            }, 200
            
        except Exception as e:
            current_app.logger.error(f"Test webhook error: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }, 500
