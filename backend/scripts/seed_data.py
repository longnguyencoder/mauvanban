"""
Database seeding script - Create sample data for testing
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import create_app
from models import db
from services import AuthService, CategoryService, DocumentService, PackageService, TransactionService


def seed_database():
    """Seed database with sample data"""
    
    app = create_app()
    
    with app.app_context():
        print("🌱 Starting database seeding...")
        
        # Create tables
        print("📦 Creating database tables...")
        db.create_all()
        
        # Create admin user
        print("👤 Creating admin user...")
        admin, error = AuthService.create_admin(
            email='admin@mauvanban.vn',
            password='admin123',
            full_name='Administrator'
        )
        
        if admin:
            print(f"   ✓ Admin created: {admin.email}")
        else:
            print(f"   ⚠ Admin creation: {error}")
        
        # Create test user
        print("👤 Creating test user...")
        user, error = AuthService.register(
            email='user@test.com',
            password='user123',
            full_name='Test User',
            phone='0123456789'
        )
        
        if user:
            print(f"   ✓ User created: {user.email}")
            # Add balance for testing
            user.balance = 1000000
            db.session.commit()
            print(f"   ✓ Added balance: 1,000,000 VND")
        else:
            print(f"   ⚠ User creation: {error}")
        
        # Create categories
        print("📁 Creating categories...")
        categories_data = [
            {'name': 'Việc làm & Nhân sự', 'icon': 'briefcase', 'display_order': 1},
            {'name': 'Giáo dục & Đào tạo', 'icon': 'graduation-cap', 'display_order': 2},
            {'name': 'Pháp luật & Tòa án', 'icon': 'gavel', 'display_order': 3},
            {'name': 'Kinh doanh & Doanh nghiệp', 'icon': 'building', 'display_order': 4},
            {'name': 'Đất đai & Bất động sản', 'icon': 'home', 'display_order': 5},
            {'name': 'Tài chính & Ngân hàng', 'icon': 'dollar-sign', 'display_order': 6},
            {'name': 'Y tế & Sức khỏe', 'icon': 'heartbeat', 'display_order': 7},
            {'name': 'Hành chính & Công vụ', 'icon': 'file-text', 'display_order': 8},
        ]
        
        created_categories = {}
        for cat_data in categories_data:
            category, error = CategoryService.create_category(**cat_data)
            if category:
                created_categories[cat_data['name']] = category
                print(f"   ✓ Category created: {category.name}")
        
        # Create sample documents
        print("📄 Creating sample documents...")
        documents_data = [
            {
                'code': 'VL-01',
                'title': 'Đơn xin việc',
                'description': 'Mẫu đơn xin việc chuẩn, chuyên nghiệp',
                'category_id': created_categories['Việc làm & Nhân sự'].id,
                'price': 10000,
                'content': 'Kính gửi: Ban Giám đốc Công ty...',
                'file_type': 'docx',
                'is_featured': True,
                'guide_data': {
                    'usage_guide': 'Sử dụng khi xin việc tại các công ty, doanh nghiệp',
                    'filling_guide': 'Điền đầy đủ thông tin cá nhân, kinh nghiệm làm việc',
                    'submission_guide': 'Nộp trực tiếp hoặc gửi qua email',
                    'required_documents': 'Sơ yếu lý lịch, bằng cấp, chứng chỉ',
                    'fees_info': 'Không mất phí',
                    'notes': 'Nên in trên giấy A4, ký tên tay'
                }
            },
            {
                'code': 'VL-02',
                'title': 'Đơn xin nghỉ phép',
                'description': 'Mẫu đơn xin nghỉ phép theo quy định',
                'category_id': created_categories['Việc làm & Nhân sự'].id,
                'price': 5000,
                'content': 'Kính gửi: Ban Lãnh đạo...',
                'file_type': 'docx',
                'is_featured': False
            },
            {
                'code': 'GD-01',
                'title': 'Đơn xin chuyển trường',
                'description': 'Mẫu đơn xin chuyển trường cho học sinh',
                'category_id': created_categories['Giáo dục & Đào tạo'].id,
                'price': 8000,
                'content': 'Kính gửi: Hiệu trưởng trường...',
                'file_type': 'docx',
                'is_featured': True
            },
            {
                'code': 'PL-01',
                'title': 'Đơn khởi kiện',
                'description': 'Mẫu đơn khởi kiện dân sự',
                'category_id': created_categories['Pháp luật & Tòa án'].id,
                'price': 50000,
                'content': 'Kính gửi: Tòa án nhân dân...',
                'file_type': 'docx',
                'is_featured': False
            },
            {
                'code': 'DN-01',
                'title': 'Hợp đồng mua bán',
                'description': 'Mẫu hợp đồng mua bán hàng hóa',
                'category_id': created_categories['Kinh doanh & Doanh nghiệp'].id,
                'price': 30000,
                'content': 'Hôm nay, ngày... tháng... năm...',
                'file_type': 'docx',
                'is_featured': True
            },
        ]
        
        created_documents = []
        for doc_data in documents_data:
            document, error = DocumentService.create_document(**doc_data)
            if document:
                created_documents.append(document)
                print(f"   ✓ Document created: {document.code} - {document.title}")
        
        # Create sample package
        print("📦 Creating sample package...")
        package, error = PackageService.create_package(
            name='Gói Văn bản Việc làm',
            description='Gói văn bản đầy đủ cho người đi làm',
            price=12000,
            discount_percent=20,
            document_ids=[doc.id for doc in created_documents[:2]]
        )
        
        if package:
            print(f"   ✓ Package created: {package.name}")
        
        print("\n✅ Database seeding completed!")
        print("\n📊 Summary:")
        print(f"   - Admin users: 1")
        print(f"   - Regular users: 1")
        print(f"   - Categories: {len(created_categories)}")
        print(f"   - Documents: {len(created_documents)}")
        print(f"   - Packages: 1")
        print("\n🔐 Login credentials:")
        print(f"   Admin: admin@mauvanban.vn / admin123")
        print(f"   User:  user@test.com / user123")


if __name__ == '__main__':
    seed_database()
