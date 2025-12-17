"""
Web scraper for mauvanban.vn
Crawl categories and documents from the website
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import db, Category, Document, DocumentGuide
from main import create_app

BASE_URL = "https://mauvanban.vn"

def crawl_categories():
    """Crawl categories from mauvanban.vn"""
    print("🔍 Crawling categories...")
    
    try:
        response = requests.get(BASE_URL, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        categories = []
        
        # Find category menu (adjust selectors based on actual website structure)
        category_links = soup.find_all('a', class_='category-link')  # Adjust selector
        
        for link in category_links:
            name = link.text.strip()
            url = link.get('href')
            
            if name and url:
                categories.append({
                    'name': name,
                    'url': url if url.startswith('http') else BASE_URL + url,
                    'slug': url.split('/')[-1] if '/' in url else name.lower().replace(' ', '-')
                })
        
        print(f"✅ Found {len(categories)} categories")
        return categories
        
    except Exception as e:
        print(f"❌ Error crawling categories: {str(e)}")
        return []


def crawl_documents(category_url, category_name, limit=10):
    """Crawl documents from a category page"""
    print(f"📄 Crawling documents from: {category_name}")
    
    try:
        response = requests.get(category_url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        documents = []
        
        # Find document links (adjust selectors based on actual website)
        doc_items = soup.find_all('div', class_='document-item')[:limit]  # Adjust selector
        
        for item in doc_items:
            try:
                title_elem = item.find('h3') or item.find('a')
                link_elem = item.find('a')
                
                if title_elem and link_elem:
                    title = title_elem.text.strip()
                    url = link_elem.get('href')
                    
                    if url:
                        doc_url = url if url.startswith('http') else BASE_URL + url
                        
                        # Crawl document detail
                        doc_data = crawl_document_detail(doc_url, title)
                        if doc_data:
                            documents.append(doc_data)
                        
                        # Be nice to the server
                        time.sleep(1)
                        
            except Exception as e:
                print(f"  ⚠️  Error parsing document: {str(e)}")
                continue
        
        print(f"  ✅ Found {len(documents)} documents")
        return documents
        
    except Exception as e:
        print(f"  ❌ Error crawling documents: {str(e)}")
        return []


def crawl_document_detail(url, title):
    """Crawl document detail page"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract document data (adjust selectors based on actual website)
        description_elem = soup.find('div', class_='description')
        content_elem = soup.find('div', class_='content')
        
        # Extract guide information
        guide_elem = soup.find('div', class_='guide')
        
        doc_data = {
            'title': title,
            'description': description_elem.text.strip() if description_elem else '',
            'content': content_elem.text.strip()[:500] if content_elem else '',  # Preview only
            'url': url,
            'guide': {}
        }
        
        # Extract guide sections
        if guide_elem:
            usage = guide_elem.find('div', class_='usage-guide')
            filling = guide_elem.find('div', class_='filling-guide')
            
            if usage:
                doc_data['guide']['usage_guide'] = usage.text.strip()
            if filling:
                doc_data['guide']['filling_guide'] = filling.text.strip()
        
        return doc_data
        
    except Exception as e:
        print(f"    ⚠️  Error crawling detail: {str(e)}")
        return None


def save_to_database(categories_data, app):
    """Save crawled data to database"""
    print("\n💾 Saving to database...")
    
    with app.app_context():
        try:
            # Create categories
            category_map = {}
            
            for cat_data in categories_data:
                category = Category.query.filter_by(slug=cat_data['slug']).first()
                
                if not category:
                    category = Category(
                        name=cat_data['name'],
                        slug=cat_data['slug'],
                        description=f"Các loại {cat_data['name'].lower()}",
                        is_active=True
                    )
                    db.session.add(category)
                    db.session.flush()
                
                category_map[cat_data['name']] = category.id
                
                # Create documents for this category
                if 'documents' in cat_data:
                    for idx, doc_data in enumerate(cat_data['documents'], 1):
                        # Generate unique code
                        code = f"{cat_data['slug'].upper()[:3]}-{idx:03d}"
                        
                        # Check if document exists
                        existing = Document.query.filter_by(code=code).first()
                        if existing:
                            continue
                        
                        document = Document(
                            code=code,
                            title=doc_data['title'],
                            description=doc_data['description'],
                            content=doc_data['content'],
                            category_id=category.id,
                            price=10000 + (idx * 1000),  # Sample pricing
                            is_featured=(idx <= 2),  # First 2 are featured
                            is_active=True
                        )
                        db.session.add(document)
                        db.session.flush()
                        
                        # Create guide if available
                        if doc_data.get('guide'):
                            guide = DocumentGuide(
                                document_id=document.id,
                                usage_guide=doc_data['guide'].get('usage_guide'),
                                filling_guide=doc_data['guide'].get('filling_guide'),
                                submission_guide="Nộp tại cơ quan có thẩm quyền",
                                required_documents="Giấy tờ tùy thân",
                                fees_info="Tùy theo quy định",
                                notes="Lưu ý kiểm tra kỹ trước khi nộp"
                            )
                            db.session.add(guide)
            
            db.session.commit()
            print("✅ Data saved successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error saving to database: {str(e)}")


def main():
    """Main crawling function"""
    print("=" * 60)
    print("🕷️  Mauvanban.vn Web Scraper")
    print("=" * 60)
    
    # Create Flask app
    app = create_app()
    
    # Crawl categories
    categories = crawl_categories()
    
    if not categories:
        print("⚠️  No categories found. Using fallback data...")
        # Fallback categories if crawling fails
        categories = [
            {'name': 'Hợp đồng', 'url': f'{BASE_URL}/hop-dong', 'slug': 'hop-dong'},
            {'name': 'Đơn từ', 'url': f'{BASE_URL}/don-tu', 'slug': 'don-tu'},
            {'name': 'Biên bản', 'url': f'{BASE_URL}/bien-ban', 'slug': 'bien-ban'},
            {'name': 'Giấy ủy quyền', 'url': f'{BASE_URL}/giay-uy-quyen', 'slug': 'giay-uy-quyen'},
        ]
    
    # Crawl documents for each category
    for category in categories[:5]:  # Limit to first 5 categories
        docs = crawl_documents(category['url'], category['name'], limit=5)
        category['documents'] = docs
        time.sleep(2)  # Be nice to the server
    
    # Save to JSON file
    output_file = 'scripts/crawled_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 Data saved to: {output_file}")
    
    # Save to database
    save_to_database(categories, app)
    
    print("\n" + "=" * 60)
    print("✅ Crawling completed!")
    print("=" * 60)


if __name__ == '__main__':
    main()
