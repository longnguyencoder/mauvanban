"""
User controller - RESTful API endpoints for user operations
FIXED: Proper decorator usage
"""
from flask import request
from flask_restx import Namespace, Resource
from services import UserService, TransactionService
from middleware import token_required

# Create namespace
user_ns = Namespace('user', description='User operations')


@user_ns.route('/saved-documents')
class SavedDocuments(Resource):
    """User saved documents endpoint"""
    
    @token_required
    @user_ns.doc(description='Get user saved documents', security='Bearer')
    @user_ns.param('page', 'Page number', type=int, default=1)
    @user_ns.param('per_page', 'Items per page', type=int, default=20)
    def get(self, current_user):
        """Get saved documents"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        result = UserService.get_saved_documents(
            current_user.id,
            page=page,
            per_page=per_page
        )
        
        return {
            'success': True,
            'data': result
        }, 200


@user_ns.route('/transactions')
class UserTransactions(Resource):
    """User transactions endpoint"""
    
    @token_required
    @user_ns.doc(description='Get user transaction history', security='Bearer')
    @user_ns.param('page', 'Page number', type=int, default=1)
    @user_ns.param('per_page', 'Items per page', type=int, default=20)
    @user_ns.param('type', 'Transaction type', enum=['document', 'package', 'topup'])
    def get(self, current_user):
        """Get transaction history"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        transaction_type = request.args.get('type')
        
        result = TransactionService.get_user_transactions(
            current_user.id,
            page=page,
            per_page=per_page,
            transaction_type=transaction_type
        )
        
        return {
            'success': True,
            'data': result
        }, 200


@user_ns.route('/purchased-documents')
class PurchasedDocuments(Resource):
    """User purchased documents endpoint"""
    
    @token_required
    @user_ns.doc(description='Get all purchased documents', security='Bearer')
    def get(self, current_user):
        """Get purchased documents"""
        documents = TransactionService.get_purchased_documents(current_user.id)
        
        return {
            'success': True,
            'data': [doc.to_dict(include_category=True) for doc in documents]
        }, 200


@user_ns.route('/topup')
class TopupBalance(Resource):
    """Top up balance endpoint"""
    
    @token_required
    @user_ns.doc(description='Top up account balance', security='Bearer')
    def post(self, current_user):
        """Top up balance"""
        data = request.json
        amount = data.get('amount', 0)
        payment_method = data.get('payment_method', 'manual')
        
        transaction, error = TransactionService.topup_balance(
            current_user.id,
            amount,
            payment_method=payment_method
        )
        
        if error:
            return {
                'success': False,
                'message': error
            }, 400
        
        return {
            'success': True,
            'message': 'Balance topped up successfully',
            'data': transaction.to_dict()
        }, 201
