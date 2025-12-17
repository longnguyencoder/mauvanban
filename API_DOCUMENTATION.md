# API Documentation - Mẫu Văn Bản

**Base URL**: `http://localhost:5000/api`  
**API Docs**: `http://localhost:5000/api/docs`

---

## 🔐 Authentication

### JWT Token Authentication

API sử dụng JWT (JSON Web Tokens) cho authentication.

**Header Format:**
```
Authorization: Bearer {access_token}
```

**Token Expiry:**
- Access Token: 1 giờ
- Refresh Token: 30 ngày

---

## 📋 API Endpoints Overview

### Public APIs (Không cần authentication)
- ✅ Xem categories
- ✅ Xem documents
- ✅ Tìm kiếm documents
- ✅ Xem chi tiết document

### User APIs (Cần login)
- 🔒 Lưu documents
- 🔒 Mua & download documents
- 🔒 Xem lịch sử giao dịch
- 🔒 Nạp tiền
- 🔒 Báo cáo vấn đề

### Admin APIs (Chỉ admin)
- 👑 Quản lý categories
- 👑 Quản lý documents
- 👑 Quản lý packages
- 👑 Quản lý users
- 👑 Xem dashboard

---

## 1️⃣ Authentication APIs

### 1.1 Đăng ký User

**Endpoint:** `POST /auth/register`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "Nguyễn Văn A",
  "phone": "0123456789"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Registration successful",
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "Nguyễn Văn A",
    "role": "user",
    "is_active": true
  }
}
```

---

### 1.2 Đăng nhập

**Endpoint:** `POST /auth/login`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "full_name": "Nguyễn Văn A",
      "role": "user",
      "balance": 0
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**Frontend Usage:**
```javascript
// Lưu tokens vào localStorage
localStorage.setItem('access_token', response.data.access_token);
localStorage.setItem('refresh_token', response.data.refresh_token);
localStorage.setItem('user', JSON.stringify(response.data.user));
```

---

### 1.3 Refresh Token

**Endpoint:** `POST /auth/refresh`

**Headers:**
```
Authorization: Bearer {refresh_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "new_access_token"
  }
}
```

---

### 1.4 Lấy thông tin User hiện tại

**Endpoint:** `GET /auth/me`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "Nguyễn Văn A",
    "phone": "0123456789",
    "role": "user",
    "balance": 100000,
    "is_active": true
  }
}
```

---

## 2️⃣ Category APIs (Public)

### 2.1 Lấy danh sách Categories (Tree)

**Endpoint:** `GET /categories/tree`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Hợp đồng",
      "slug": "hop-dong",
      "icon": "file-contract",
      "children": [
        {
          "id": "uuid",
          "name": "Hợp đồng thuê nhà",
          "slug": "hop-dong-thue-nha",
          "parent_id": "parent-uuid"
        }
      ],
      "documents_count": 5
    }
  ]
}
```

**Frontend Usage:**
```javascript
// Hiển thị menu categories
const renderCategoryMenu = (categories) => {
  return categories.map(cat => (
    <li key={cat.id}>
      <Link to={`/category/${cat.slug}`}>
        <i className={cat.icon}></i>
        {cat.name} ({cat.documents_count})
      </Link>
      {cat.children && renderCategoryMenu(cat.children)}
    </li>
  ));
};
```

---

### 2.2 Lấy Documents trong Category

**Endpoint:** `GET /categories/{slug}/documents`

**Query Params:**
- `page` (int): Trang hiện tại (default: 1)
- `per_page` (int): Số items/trang (default: 20)

**Response:**
```json
{
  "success": true,
  "data": {
    "documents": [...],
    "total": 50,
    "page": 1,
    "per_page": 20,
    "pages": 3
  }
}
```

---

## 3️⃣ Document APIs

### 3.1 Danh sách Documents

**Endpoint:** `GET /documents`

**Query Params:**
- `page` (int): Trang
- `per_page` (int): Số items/trang
- `category_id` (string): Lọc theo category
- `is_featured` (boolean): Lọc featured
- `search` (string): Tìm kiếm
- `sort_by` (string): `created_at`, `views_count`, `downloads_count`, `price`
- `sort_order` (string): `asc`, `desc`

**Example:**
```
GET /documents?page=1&per_page=20&is_featured=true&sort_by=views_count&sort_order=desc
```

**Response:**
```json
{
  "success": true,
  "data": {
    "documents": [
      {
        "id": "uuid",
        "code": "HD-01",
        "title": "Hợp đồng thuê nhà",
        "slug": "hop-dong-thue-nha",
        "description": "Mẫu hợp đồng...",
        "price": 20000,
        "views_count": 150,
        "downloads_count": 45,
        "is_featured": true,
        "category": {
          "id": "uuid",
          "name": "Hợp đồng",
          "slug": "hop-dong"
        }
      }
    ],
    "total": 100,
    "page": 1,
    "per_page": 20,
    "pages": 5
  }
}
```

**Frontend Usage:**
```javascript
// Fetch documents với pagination
const fetchDocuments = async (page = 1, filters = {}) => {
  const params = new URLSearchParams({
    page,
    per_page: 20,
    ...filters
  });
  
  const response = await fetch(`/api/documents?${params}`);
  const data = await response.json();
  
  return data.data;
};
```

---

### 3.2 Tìm kiếm Documents

**Endpoint:** `GET /documents/search`

**Query Params:**
- `q` (string, required): Từ khóa tìm kiếm
- `page` (int)
- `per_page` (int)

**Example:**
```
GET /documents/search?q=hợp đồng thuê&page=1
```

---

### 3.3 Chi tiết Document

**Endpoint:** `GET /documents/{slug}`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "code": "HD-01",
    "title": "Hợp đồng thuê nhà",
    "slug": "hop-dong-thue-nha",
    "description": "Mẫu hợp đồng...",
    "content": "CỘNG HÒA XÃ HỘI CHỦ NGHĨA...",
    "price": 20000,
    "views_count": 151,
    "file_type": "docx",
    "category": {...},
    "guide": {
      "usage_guide": "Sử dụng khi...",
      "filling_guide": "Điền đầy đủ...",
      "submission_guide": "In 2 bản...",
      "required_documents": "CMND/CCCD...",
      "fees_info": "Không mất phí",
      "notes": "Nên có người làm chứng"
    },
    "has_purchased": false
  }
}
```

**Frontend Usage:**
```javascript
// Hiển thị document detail
const DocumentDetail = ({ slug }) => {
  const [doc, setDoc] = useState(null);
  
  useEffect(() => {
    fetch(`/api/documents/${slug}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    .then(res => res.json())
    .then(data => setDoc(data.data));
  }, [slug]);
  
  return (
    <div>
      <h1>{doc?.title}</h1>
      <p>Giá: {doc?.price.toLocaleString()} VND</p>
      {doc?.has_purchased ? (
        <button onClick={handleDownload}>Download</button>
      ) : (
        <button onClick={handlePurchase}>Mua ngay</button>
      )}
    </div>
  );
};
```

---

### 3.4 Lưu Document (Bookmark)

**Endpoint:** `POST /documents/{id}/save`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "message": "Document saved successfully"
}
```

---

### 3.5 Bỏ lưu Document

**Endpoint:** `DELETE /documents/{id}/save`

**Headers:**
```
Authorization: Bearer {access_token}
```

---

### 3.6 Mua & Download Document

**Endpoint:** `POST /documents/{id}/download`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "message": "Document ready for download",
  "data": {
    "file_url": "/uploads/documents/HD-01.docx",
    "file_type": "docx"
  }
}
```

**Frontend Usage:**
```javascript
const handlePurchase = async (documentId) => {
  try {
    const response = await fetch(`/api/documents/${documentId}/download`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Download file
      window.location.href = data.data.file_url;
    } else {
      alert(data.message); // "Insufficient balance" hoặc lỗi khác
    }
  } catch (error) {
    console.error(error);
  }
};
```

---

## 4️⃣ User APIs

### 4.1 Xem Documents đã lưu

**Endpoint:** `GET /user/saved-documents`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Params:**
- `page` (int)
- `per_page` (int)

---

### 4.2 Lịch sử giao dịch

**Endpoint:** `GET /user/transactions`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Params:**
- `page` (int)
- `per_page` (int)
- `type` (string): `document`, `package`, `topup`

**Response:**
```json
{
  "success": true,
  "data": {
    "transactions": [
      {
        "id": "uuid",
        "transaction_type": "document",
        "amount": 20000,
        "status": "completed",
        "created_at": "2025-12-17T10:30:00",
        "document": {
          "title": "Hợp đồng thuê nhà"
        }
      }
    ],
    "total": 10,
    "page": 1,
    "pages": 1
  }
}
```

---

### 4.3 Nạp tiền

**Endpoint:** `POST /user/topup`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request:**
```json
{
  "amount": 100000,
  "payment_method": "manual"
}
```

---

## 5️⃣ Package APIs

### 5.1 Danh sách Packages

**Endpoint:** `GET /packages`

**Query Params:**
- `page` (int)
- `per_page` (int)

---

### 5.2 Chi tiết Package

**Endpoint:** `GET /packages/{slug}`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Gói Văn bản Việc làm",
    "slug": "goi-van-ban-viec-lam",
    "description": "Gói văn bản đầy đủ...",
    "price": 12000,
    "discount_percent": 20,
    "final_price": 9600,
    "documents": [
      {...},
      {...}
    ]
  }
}
```

---

### 5.3 Mua Package

**Endpoint:** `POST /packages/{id}/purchase`

**Headers:**
```
Authorization: Bearer {access_token}
```

---

## 🔴 Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "message": "Email already registered"
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "message": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "success": false,
  "message": "Admin access required"
}
```

### 404 Not Found
```json
{
  "success": false,
  "message": "Document not found"
}
```

---

## 💻 Frontend Integration Examples

### React + Axios

```javascript
// api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api'
});

// Add token to requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh
api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');
      
      try {
        const { data } = await axios.post('/api/auth/refresh', {}, {
          headers: { Authorization: `Bearer ${refreshToken}` }
        });
        
        localStorage.setItem('access_token', data.data.access_token);
        error.config.headers.Authorization = `Bearer ${data.data.access_token}`;
        
        return api(error.config);
      } catch {
        // Redirect to login
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

### Vue 3 + Composition API

```javascript
// useDocuments.js
import { ref } from 'vue';
import api from './api';

export function useDocuments() {
  const documents = ref([]);
  const loading = ref(false);
  
  const fetchDocuments = async (filters = {}) => {
    loading.value = true;
    try {
      const { data } = await api.get('/documents', { params: filters });
      documents.value = data.data.documents;
    } catch (error) {
      console.error(error);
    } finally {
      loading.value = false;
    }
  };
  
  return { documents, loading, fetchDocuments };
}
```

---

## 📱 Response Format

Tất cả responses đều theo format:

```json
{
  "success": boolean,
  "message": string,  // Optional
  "data": object | array
}
```

---

## 🔧 Testing với cURL

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@mauvanban.vn","password":"Admin@123"}'

# Get documents
curl http://localhost:5000/api/documents

# Create category (admin)
curl -X POST http://localhost:5000/api/admin/categories \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Category","description":"Test"}'
```

---

## 📊 Rate Limiting

Hiện tại chưa có rate limiting. Sẽ implement trong tương lai.

---

## 🔗 Useful Links

- **Swagger UI**: http://localhost:5000/api/docs
- **Health Check**: http://localhost:5000/health
- **Base API**: http://localhost:5000/api
