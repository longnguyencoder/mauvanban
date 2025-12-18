"""
SePay Payment Controller
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
            
            payment_info, error = TransactionService.create_sepay_payment(current_user.id, item_type, item_id)
            
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
            return {
                'success': False,
                'message': 'Failed to create payment'
            }, 500


@sepay_ns.route('/webhook')
class SepayWebhook(Resource):
    """SePay webhook endpoint"""
    
    @sepay_ns.doc(description='Receive webhook from SePay')
    def post(self):
        """Process SePay webhook"""
        try:
            # Get raw payload and signature
            payload = request.get_data(as_text=True)
            signature = request.headers.get('X-Sepay-Signature', '')
            
            current_app.logger.info(f"SePay webhook received")
            
            # Verify signature
            if not SepayService.verify_webhook_signature(payload, signature):
                current_app.logger.warning("Invalid SePay webhook signature")
                return {
                    'success': False,
                    'message': 'Invalid signature'
                }, 401
            
            # Parse JSON data
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                return {
                    'success': False,
                    'message': 'Invalid JSON payload'
                }, 400
            
            # Process webhook
            success, message = SepayService.process_payment_webhook(data)
            
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
            current_app.logger.error(f"SePay webhook error: {str(e)}")
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
            result, error = SepayService.check_transaction_status(transaction_id)
            
            if error:
                return {
                    'success': False,
                    'message': error
                }, 404
            
            return {
                'success': True,
                'data': result
            }, 200
            
        except Exception as e:
            current_app.logger.error(f"SePay check error: {str(e)}")
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
            return {
                'success': False,
                'message': 'Failed to cancel payment'
            }, 500
