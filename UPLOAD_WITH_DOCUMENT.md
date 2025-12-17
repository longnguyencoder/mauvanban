# Upload File Kèm Document - Hướng Dẫn

## 📤 Tạo Document + Upload File Trong 1 Request

Bây giờ bạn có thể upload file và tạo document cùng lúc!

---

## API Endpoint

**Endpoint:** `POST /api/admin/documents`

**Headers:**
```
Authorization: Bearer {admin_access_token}
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: File PDF/Word/Excel (optional)
- `code`: Mã document (required)
- `title`: Tiêu đề (required)
- `category_id`: ID category (required)
- `description`: Mô tả
- `price`: Giá tiền
- `content`: Nội dung preview
- `is_featured`: true/false
- `meta_keywords`: SEO keywords
- `meta_description`: SEO description
- `guide`: JSON string chứa hướng dẫn

---

## Frontend Integration

### React + Axios

```javascript
const createDocumentWithFile = async (file, documentData) => {
  const formData = new FormData();
  
  // Add file
  if (file) {
    formData.append('file', file);
  }
  
  // Add document data
  formData.append('code', documentData.code);
  formData.append('title', documentData.title);
  formData.append('category_id', documentData.category_id);
  formData.append('description', documentData.description || '');
  formData.append('price', documentData.price || 0);
  formData.append('content', documentData.content || '');
  formData.append('is_featured', documentData.is_featured || false);
  formData.append('meta_keywords', documentData.meta_keywords || '');
  formData.append('meta_description', documentData.meta_description || '');
  
  // Add guide as JSON string
  if (documentData.guide) {
    formData.append('guide', JSON.stringify(documentData.guide));
  }
  
  try {
    const response = await axios.post('/api/admin/documents', formData, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'multipart/form-data'
      }
    });
    
    return response.data.data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
};

// Usage
const handleSubmit = async (e) => {
  e.preventDefault();
  
  const file = document.getElementById('fileInput').files[0];
  
  const documentData = {
    code: 'HD-01',
    title: 'Hợp đồng thuê nhà',
    description: 'Mẫu hợp đồng thuê nhà chuẩn',
    category_id: '99820a30-a4ff-47c8-832f-c7e3fe0455b5',
    price: 20000,
    content: 'CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM...',
    is_featured: true,
    meta_keywords: 'hợp đồng, thuê nhà',
    meta_description: 'Mẫu hợp đồng thuê nhà',
    guide: {
      usage_guide: 'Sử dụng khi thuê nhà',
      filling_guide: 'Điền đầy đủ thông tin',
      submission_guide: 'In 2 bản, ký tên',
      required_documents: 'CMND/CCCD',
      fees_info: 'Không mất phí',
      notes: 'Nên có người làm chứng'
    }
  };
  
  const document = await createDocumentWithFile(file, documentData);
  console.log('Document created:', document);
};
```

---

### React Component Example

```jsx
import { useState } from 'react';
import axios from 'axios';

const CreateDocumentForm = () => {
  const [file, setFile] = useState(null);
  const [formData, setFormData] = useState({
    code: '',
    title: '',
    category_id: '',
    description: '',
    price: 0,
    content: '',
    is_featured: false,
    meta_keywords: '',
    meta_description: ''
  });
  
  const [guide, setGuide] = useState({
    usage_guide: '',
    filling_guide: '',
    submission_guide: '',
    required_documents: '',
    fees_info: '',
    notes: ''
  });
  
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };
  
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };
  
  const handleGuideChange = (e) => {
    const { name, value } = e.target;
    setGuide(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const data = new FormData();
    
    // Add file
    if (file) {
      data.append('file', file);
    }
    
    // Add form fields
    Object.keys(formData).forEach(key => {
      data.append(key, formData[key]);
    });
    
    // Add guide as JSON
    data.append('guide', JSON.stringify(guide));
    
    try {
      const response = await axios.post('/api/admin/documents', data, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      
      alert('Document created successfully!');
      console.log(response.data.data);
    } catch (error) {
      alert('Error: ' + error.response?.data?.message);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <h2>Tạo Document Mới</h2>
      
      {/* File Upload */}
      <div>
        <label>File PDF/Word:</label>
        <input 
          type="file" 
          accept=".pdf,.doc,.docx,.xls,.xlsx"
          onChange={handleFileChange}
        />
      </div>
      
      {/* Basic Info */}
      <div>
        <label>Mã:</label>
        <input 
          name="code" 
          value={formData.code}
          onChange={handleInputChange}
          required
        />
      </div>
      
      <div>
        <label>Tiêu đề:</label>
        <input 
          name="title" 
          value={formData.title}
          onChange={handleInputChange}
          required
        />
      </div>
      
      <div>
        <label>Category ID:</label>
        <input 
          name="category_id" 
          value={formData.category_id}
          onChange={handleInputChange}
          required
        />
      </div>
      
      <div>
        <label>Mô tả:</label>
        <textarea 
          name="description" 
          value={formData.description}
          onChange={handleInputChange}
        />
      </div>
      
      <div>
        <label>Giá:</label>
        <input 
          type="number" 
          name="price" 
          value={formData.price}
          onChange={handleInputChange}
        />
      </div>
      
      <div>
        <label>Nội dung preview:</label>
        <textarea 
          name="content" 
          value={formData.content}
          onChange={handleInputChange}
        />
      </div>
      
      <div>
        <label>
          <input 
            type="checkbox" 
            name="is_featured" 
            checked={formData.is_featured}
            onChange={handleInputChange}
          />
          Featured
        </label>
      </div>
      
      {/* Guide */}
      <h3>Hướng dẫn</h3>
      
      <div>
        <label>Hướng dẫn sử dụng:</label>
        <textarea 
          name="usage_guide" 
          value={guide.usage_guide}
          onChange={handleGuideChange}
        />
      </div>
      
      <div>
        <label>Hướng dẫn điền:</label>
        <textarea 
          name="filling_guide" 
          value={guide.filling_guide}
          onChange={handleGuideChange}
        />
      </div>
      
      <div>
        <label>Hướng dẫn nộp:</label>
        <textarea 
          name="submission_guide" 
          value={guide.submission_guide}
          onChange={handleGuideChange}
        />
      </div>
      
      <div>
        <label>Giấy tờ cần thiết:</label>
        <textarea 
          name="required_documents" 
          value={guide.required_documents}
          onChange={handleGuideChange}
        />
      </div>
      
      <div>
        <label>Thông tin phí:</label>
        <textarea 
          name="fees_info" 
          value={guide.fees_info}
          onChange={handleGuideChange}
        />
      </div>
      
      <div>
        <label>Ghi chú:</label>
        <textarea 
          name="notes" 
          value={guide.notes}
          onChange={handleGuideChange}
        />
      </div>
      
      <button type="submit">Tạo Document</button>
    </form>
  );
};

export default CreateDocumentForm;
```

---

### Vue 3 Example

```vue
<template>
  <form @submit.prevent="handleSubmit">
    <h2>Tạo Document Mới</h2>
    
    <div>
      <label>File:</label>
      <input type="file" @change="handleFileChange" accept=".pdf,.doc,.docx" />
    </div>
    
    <div>
      <label>Mã:</label>
      <input v-model="formData.code" required />
    </div>
    
    <div>
      <label>Tiêu đề:</label>
      <input v-model="formData.title" required />
    </div>
    
    <div>
      <label>Category ID:</label>
      <input v-model="formData.category_id" required />
    </div>
    
    <div>
      <label>Giá:</label>
      <input type="number" v-model="formData.price" />
    </div>
    
    <button type="submit">Tạo Document</button>
  </form>
</template>

<script setup>
import { ref } from 'vue';
import api from './api';

const file = ref(null);
const formData = ref({
  code: '',
  title: '',
  category_id: '',
  description: '',
  price: 0,
  content: '',
  is_featured: false
});

const handleFileChange = (e) => {
  file.value = e.target.files[0];
};

const handleSubmit = async () => {
  const data = new FormData();
  
  if (file.value) {
    data.append('file', file.value);
  }
  
  Object.keys(formData.value).forEach(key => {
    data.append(key, formData.value[key]);
  });
  
  try {
    const response = await api.post('/admin/documents', data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    alert('Success!');
    console.log(response.data.data);
  } catch (error) {
    alert('Error: ' + error.response?.data?.message);
  }
};
</script>
```

---

## Testing với Postman

1. **Method**: `POST`
2. **URL**: `http://localhost:5000/api/admin/documents`
3. **Headers**:
   - `Authorization: Bearer {your_admin_token}`
4. **Body** → Select `form-data`:
   - `file` (File): Chọn file PDF/Word
   - `code` (Text): `HD-01`
   - `title` (Text): `Hợp đồng thuê nhà`
   - `category_id` (Text): `99820a30-a4ff-47c8-832f-c7e3fe0455b5`
   - `price` (Text): `20000`
   - `description` (Text): `Mẫu hợp đồng...`
   - `content` (Text): `CỘNG HÒA...`
   - `is_featured` (Text): `true`
   - `guide` (Text): `{"usage_guide":"Sử dụng khi...","filling_guide":"Điền..."}`

5. **Send**

---

## Testing với cURL

```bash
curl -X POST http://localhost:5000/api/admin/documents \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@/path/to/document.pdf" \
  -F "code=HD-01" \
  -F "title=Hợp đồng thuê nhà" \
  -F "category_id=99820a30-a4ff-47c8-832f-c7e3fe0455b5" \
  -F "price=20000" \
  -F "description=Mẫu hợp đồng thuê nhà" \
  -F "content=CỘNG HÒA XÃ HỘI CHỦ NGHĨA..." \
  -F "is_featured=true" \
  -F 'guide={"usage_guide":"Sử dụng khi thuê nhà","filling_guide":"Điền đầy đủ thông tin"}'
```

---

## Response

```json
{
  "success": true,
  "message": "Document created successfully",
  "data": {
    "id": "uuid",
    "code": "HD-01",
    "title": "Hợp đồng thuê nhà",
    "file_url": "/uploads/documents/abc123_20251217.pdf",
    "file_type": "pdf",
    "price": 20000,
    "guide": {
      "usage_guide": "Sử dụng khi thuê nhà",
      "filling_guide": "Điền đầy đủ thông tin",
      ...
    }
  }
}
```

---

## Lưu ý

- ✅ File upload là **optional** - có thể tạo document không có file
- ✅ Nếu có file, sẽ tự động upload và set `file_url`
- ✅ `guide` phải là JSON string trong form data
- ✅ `is_featured` nhận giá trị `true`/`false` (string)
- ✅ Hỗ trợ cả JSON và multipart/form-data

---

## So sánh 2 cách

### Cách 1: Upload riêng (2 requests)
```javascript
// Step 1: Upload file
const uploadedFile = await uploadFile(file);

// Step 2: Create document
const document = await createDocument({
  ...data,
  file_url: uploadedFile.file_url
});
```

### Cách 2: Upload kèm document (1 request) ✅
```javascript
// All in one
const document = await createDocumentWithFile(file, data);
```

**Khuyên dùng Cách 2** - Đơn giản hơn và nhanh hơn!
