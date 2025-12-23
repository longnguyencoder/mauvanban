import requests
import json
from flask import current_app
from models import db, News
from datetime import datetime

class NewsService:
    @staticmethod
    def generate_content(topic, keywords):
        """
        Generate news content using Hugging Face Inference API (Qwen2-7B-Instruct)
        """
        api_key = current_app.config.get('HUGGINGFACE_API_KEY')
        model = current_app.config.get('HUGGINGFACE_MODEL_NEWS')
        
        if not api_key:
            return {"error": "Hugging Face API Key is not configured"}, 400

        api_url = f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Authorization": f"Bearer {api_key}"}

        prompt = f"""<|im_start|>system
Bạn là một chuyên gia viết nội dung (Content Writer) và Marketing giàu kinh nghiệm tại Việt Nam. 
Nhiệm vụ của bạn là viết một bài giới thiệu dịch vụ hoặc bài tin tức chuyên nghiệp, thu hút người đọc và tối ưu SEO.
Yêu cầu:
1. Ngôn ngữ: Tiếng Việt chuyên nghiệp, lịch sự.
2. Cấu trúc bài viết:
   - Một tiêu đề hấp dẫn (Headline).
   - Một đoạn tóm tắt ngắn (Summary).
   - Nội dung chi tiết được trình bày bằng HTML (sử dụng các thẻ <h3>, <p>, <ul>, <li>, <strong>).
   - KHÔNG bao gồm các thẻ <html>, <body>, <head>. Chỉ lấy từ tiêu đề trở đi.
3. Phong cách: Văn phong trang trọng nhưng vẫn gần gũi, tập trung vào lợi ích khách hàng.<|im_end|>
<|im_start|>user
Hãy viết một bài viết với chủ đề: "{topic}".
Các từ khóa cần bao gồm: {keywords}.
Hãy trình bày kết quả dưới định dạng JSON như sau:
{{
  "title": "Tiêu đề bài viết",
  "summary": "Mô tả ngắn gọn khoảng 2 câu",
  "content": "Nội dung bài viết đầy đủ với các thẻ HTML"
}}<|im_end|>
<|im_start|>assistant
"""
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1500,
                "temperature": 0.7,
                "top_p": 0.9,
                "return_full_text": False
            }
        }

        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            # Extract text from response
            generated_text = result[0]['generated_text']
            
            # Try to parse JSON from AI response
            try:
                # Find JSON block in case AI added extra text
                start_idx = generated_text.find('{')
                end_idx = generated_text.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = generated_text[start_idx:end_idx]
                    return json.loads(json_str), 200
                return {"error": "AI response was not in valid JSON format"}, 500
            except Exception as e:
                return {"error": f"Failed to parse AI response: {str(e)}"}, 500

        except Exception as e:
            return {"error": f"API request failed: {str(e)}"}, 500

    @staticmethod
    def create_news(data):
        """Save news to database"""
        try:
            news = News(
                title=data.get('title'),
                summary=data.get('summary'),
                content=data.get('content'),
                thumbnail_url=data.get('thumbnail_url'),
                author=data.get('author', 'Hệ thống AI')
            )
            news.generate_slug()
            db.session.add(news)
            db.session.commit()
            return news, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

    @staticmethod
    def get_all_news(page=1, per_page=10):
        """Get paginated news list"""
        pagination = News.query.filter_by(is_active=True)\
            .order_by(News.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        return pagination

    @staticmethod
    def get_news_by_slug(slug):
        """Get single news by slug"""
        news = News.query.filter_by(slug=slug, is_active=True).first()
        if news:
            news.views_count += 1
            db.session.commit()
        return news
