from flask import request
from flask_restx import Namespace, Resource, fields
from services.news_service import NewsService
from flask_jwt_extended import jwt_required, get_jwt_identity

news_ns = Namespace('news', description='News and AI Content Generation operations')

# Request and Response models
news_model = news_ns.model('News', {
    'id': fields.String(readOnly=True),
    'title': fields.String(required=True),
    'slug': fields.String(readOnly=True),
    'summary': fields.String(),
    'content': fields.String(required=True),
    'thumbnail_url': fields.String(),
    'author': fields.String(),
    'views_count': fields.Integer(readOnly=True),
    'created_at': fields.DateTime(readOnly=True)
})

generate_request = news_ns.model('GenerateNews', {
    'topic': fields.String(required=True, description='The main topic of the article'),
    'keywords': fields.String(required=True, description='Key terms to include')
})

@news_ns.route('/')
class NewsList(Resource):
    def get(self):
        """Get all news articles"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        pagination = NewsService.get_all_news(page, per_page)
        
        return {
            'success': True,
            'data': [news.to_dict() for news in pagination.items],
            'pagination': {
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': pagination.page,
                'per_page': pagination.per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }, 200

    @news_ns.expect(news_model)
    @jwt_required()
    def post(self):
        """Create a new news article manually"""
        data = request.json
        news, status = NewsService.create_news(data)
        
        if status == 201:
            return {
                'success': True,
                'message': 'News created successfully',
                'data': news.to_dict()
            }, 201
        return {
            'success': False,
            'message': news.get('error')
        }, status

@news_ns.route('/<slug>')
class NewsDetail(Resource):
    def get(self, slug):
        """Get news details by slug"""
        news = NewsService.get_news_by_slug(slug)
        if news:
            return {
                'success': True,
                'data': news.to_dict()
            }, 200
        return {
            'success': False,
            'message': 'News not found'
        }, 404

@news_ns.route('/generate')
class NewsGenerate(Resource):
    @news_ns.expect(generate_request)
    @jwt_required()
    def post(self):
        """Generate news content using AI (Hugging Face / Qwen2)"""
        data = request.json
        topic = data.get('topic')
        keywords = data.get('keywords')
        
        if not topic or not keywords:
            return {
                'success': False,
                'message': 'Topic and keywords are required'
            }, 400
            
        result, status = NewsService.generate_content(topic, keywords)
        
        if status == 200:
            return {
                'success': True,
                'data': result
            }, 200
            
        return {
            'success': False,
            'message': result.get('error', 'Failed to generate content')
        }, status
