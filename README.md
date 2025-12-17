# Mẫu Văn Bản API

Backend API RESTful cho hệ thống quản lý và phân phối mẫu văn bản, tương tự mauvanban.vn

## 🚀 Tính năng

### Phân quyền
- **Admin**: Toàn quyền quản lý categories, documents, packages, users
- **User**: Xem, tìm kiếm, lưu, mua, download documents
- **Guest**: Chỉ xem và tìm kiếm

### Chức năng chính
- ✅ Quản lý danh mục văn bản (phân cấp)
- ✅ Quản lý văn bản với hướng dẫn chi tiết
- ✅ Tìm kiếm và lọc văn bản
- ✅ Gói văn bản (bundle nhiều documents)
- ✅ Hệ thống thanh toán và giao dịch
- ✅ Lưu văn bản yêu thích
- ✅ Báo cáo vấn đề
- ✅ Thống kê và dashboard admin

## 📋 Yêu cầu

- Python 3.8+
- PostgreSQL 12+

## 🛠️ Cài đặt

### 1. Clone repository

```bash
cd mauvanban
```

### 2. Tạo virtual environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình môi trường

Tạo file `.env` từ `.env.example`:

```bash
copy .env.example .env
```

Chỉnh sửa `.env` với thông tin database của bạn:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/mauvanban_db
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
```

### 5. Tạo database

```bash
# Tạo database trong PostgreSQL
createdb mauvanban_db
```

### 6. Chạy migrations

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 7. Tạo tài khoản Admin

**Option 1: Chỉ tạo admin (nhanh)**

```bash
python scripts/create_admin.py
```

Thông tin đăng nhập:
- Email: `admin@mauvanban.vn`
- Password: `Admin@123`

**Option 2: Seed đầy đủ dữ liệu mẫu (admin + categories + documents)**

```bash
python scripts/seed_data.py
```

### 8. Chạy server

```bash
python main.py
```

Server sẽ chạy tại: `http://localhost:5000`

## 📚 API Documentation

Swagger UI: `http://localhost:5000/api/docs`

### Endpoints chính

#### Authentication (`/api/auth`)
- `POST /register` - Đăng ký user mới
- `POST /login` - Đăng nhập
- `POST /refresh` - Refresh token
- `GET /me` - Thông tin user hiện tại
- `PUT /profile` - Cập nhật profile
- `POST /change-password` - Đổi mật khẩu

#### Categories (`/api/categories`)
- `GET /` - Danh sách categories
- `GET /tree` - Category tree
- `GET /:slug` - Chi tiết category
- `GET /:slug/documents` - Documents trong category

#### Documents (`/api/documents`)
- `GET /` - Danh sách documents (có filter, sort, pagination)
- `GET /search` - Tìm kiếm documents
- `GET /:slug` - Chi tiết document
- `POST /:id/save` - Lưu document
- `POST /:id/download` - Mua và download
- `POST /:id/report` - Báo cáo vấn đề

#### Packages (`/api/packages`)
- `GET /` - Danh sách packages
- `GET /:slug` - Chi tiết package
- `POST /:id/purchase` - Mua package

#### User (`/api/user`)
- `GET /saved-documents` - Documents đã lưu
- `GET /transactions` - Lịch sử giao dịch
- `GET /purchased-documents` - Documents đã mua
- `POST /topup` - Nạp tiền

#### Admin (`/api/admin`)
- **Categories**: CRUD operations
- **Documents**: CRUD operations
- **Packages**: CRUD operations
- **Users**: Quản lý users
- **Reports**: Xử lý báo cáo
- **Dashboard**: Thống kê

## 🔐 Authentication

API sử dụng JWT (JSON Web Tokens) cho authentication.

### Cách sử dụng:

1. Login để nhận access token:
```bash
POST /api/auth/login
{
  "email": "user@test.com",
  "password": "user123"
}
```

2. Sử dụng token trong header:
```
Authorization: Bearer <your_access_token>
```

### Test accounts:
- **Admin**: `admin@mauvanban.vn` / `admin123`
- **User**: `user@test.com` / `user123`

## 🗂️ Cấu trúc dự án

```
mauvanban/
├── config/              # Cấu hình ứng dụng
├── models/              # Database models
├── services/            # Business logic
├── controllers/         # API endpoints
├── middleware/          # Authentication middleware
├── migrations/          # Database migrations
├── scripts/             # Utility scripts
├── uploads/             # File uploads
├── main.py             # Entry point
├── requirements.txt    # Dependencies
└── README.md
```

## 🧪 Testing

### Test với Swagger UI

1. Mở `http://localhost:5000/api/docs`
2. Click "Authorize" và nhập JWT token
3. Test các endpoints

### Test với curl

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"user123"}'

# Get documents
curl http://localhost:5000/api/documents

# Get categories
curl http://localhost:5000/api/categories/tree
```

## 📝 License

MIT License

## 👥 Author

Your Name - Backend Developer
