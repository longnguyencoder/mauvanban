# File Upload Guide

## 📤 Upload Document Files

API hỗ trợ upload file PDF, DOC, DOCX, XLS, XLSX cho documents.

---

## API Endpoint

### Upload File

**Endpoint:** `POST /upload/document`

**Headers:**
```
Authorization: Bearer {admin_access_token}
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: File to upload (PDF, DOC, DOCX, XLS, XLSX)

**Response:**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "data": {
    "filename": "abc123_20251217_110000.pdf",
    "original_filename": "hop-dong-thue-nha.pdf",
    "file_url": "/uploads/documents/abc123_20251217_110000.pdf",
    "file_type": "pdf",
    "file_size": 245678
  }
}
```

---

## Frontend Integration

### React + Axios

```javascript
const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await axios.post('/api/upload/document', formData, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'multipart/form-data'
      }
    });
    
    return response.data.data; // { file_url, filename, ... }
  } catch (error) {
    console.error('Upload failed:', error);
    throw error;
  }
};

// Usage in component
const handleFileUpload = async (e) => {
  const file = e.target.files[0];
  
  if (!file) return;
  
  try {
    const uploadedFile = await uploadDocument(file);
    console.log('File URL:', uploadedFile.file_url);
    
    // Use file_url when creating document
    setFileUrl(uploadedFile.file_url);
  } catch (error) {
    alert('Upload failed');
  }
};

// JSX
<input 
  type="file" 
  accept=".pdf,.doc,.docx,.xls,.xlsx"
  onChange={handleFileUpload}
/>
```

---

### Vue 3

```javascript
<template>
  <div>
    <input 
      type="file" 
      @change="handleUpload"
      accept=".pdf,.doc,.docx,.xls,.xlsx"
    />
    <p v-if="uploading">Uploading...</p>
    <p v-if="fileUrl">File uploaded: {{ fileUrl }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from './api';

const uploading = ref(false);
const fileUrl = ref('');

const handleUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  const formData = new FormData();
  formData.append('file', file);
  
  uploading.value = true;
  
  try {
    const { data } = await api.post('/upload/document', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    fileUrl.value = data.data.file_url;
  } catch (error) {
    console.error(error);
  } finally {
    uploading.value = false;
  }
};
</script>
```

---

### Vanilla JavaScript

```javascript
const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:5000/api/upload/document', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    },
    body: formData
  });
  
  const data = await response.json();
  return data.data;
};

// Usage
document.getElementById('fileInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  
  try {
    const result = await uploadFile(file);
    console.log('Uploaded:', result.file_url);
  } catch (error) {
    console.error('Upload failed:', error);
  }
});
```

---

## Complete Workflow: Create Document with File

```javascript
// Step 1: Upload file
const uploadAndCreateDocument = async (file, documentData) => {
  try {
    // 1. Upload file first
    const uploadedFile = await uploadDocument(file);
    
    // 2. Create document with file URL
    const response = await axios.post('/api/admin/documents', {
      ...documentData,
      file_url: uploadedFile.file_url,
      file_type: uploadedFile.file_type
    }, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    
    return response.data.data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
};

// Usage
const createDocumentWithFile = async () => {
  const file = document.getElementById('fileInput').files[0];
  
  const documentData = {
    code: 'HD-01',
    title: 'Hợp đồng thuê nhà',
    description: 'Mẫu hợp đồng...',
    category_id: 'category-uuid',
    price: 20000,
    content: 'Preview content...',
    is_featured: true
  };
  
  const document = await uploadAndCreateDocument(file, documentData);
  console.log('Document created:', document);
};
```

---

## Download Uploaded File

Sau khi user mua document, họ có thể download file:

```javascript
const downloadDocument = async (documentId) => {
  try {
    // Purchase document
    const response = await axios.post(`/api/documents/${documentId}/download`, {}, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    
    const { file_url } = response.data.data;
    
    // Download file
    window.location.href = `http://localhost:5000${file_url}`;
    
    // Or open in new tab
    // window.open(`http://localhost:5000${file_url}`, '_blank');
  } catch (error) {
    if (error.response?.status === 400) {
      alert(error.response.data.message); // "Insufficient balance"
    }
  }
};
```

---

## Delete Uploaded File

**Endpoint:** `DELETE /upload/document/{filename}`

```javascript
const deleteUploadedFile = async (filename) => {
  try {
    await axios.delete(`/api/upload/document/${filename}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    
    console.log('File deleted');
  } catch (error) {
    console.error('Delete failed:', error);
  }
};
```

---

## File Validation

### Allowed Extensions
- PDF: `.pdf`
- Word: `.doc`, `.docx`
- Excel: `.xls`, `.xlsx`

### Max File Size
Configured in `.env`:
```
MAX_CONTENT_LENGTH=16777216  # 16MB
```

### Frontend Validation

```javascript
const validateFile = (file) => {
  const allowedTypes = ['application/pdf', 'application/msword', 
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
  
  const maxSize = 16 * 1024 * 1024; // 16MB
  
  if (!allowedTypes.includes(file.type)) {
    alert('Invalid file type. Only PDF, DOC, DOCX, XLS, XLSX allowed.');
    return false;
  }
  
  if (file.size > maxSize) {
    alert('File too large. Max size: 16MB');
    return false;
  }
  
  return true;
};

// Usage
const handleFileChange = (e) => {
  const file = e.target.files[0];
  
  if (validateFile(file)) {
    uploadDocument(file);
  }
};
```

---

## Error Handling

```javascript
const uploadWithErrorHandling = async (file) => {
  try {
    const result = await uploadDocument(file);
    return result;
  } catch (error) {
    if (error.response) {
      switch (error.response.status) {
        case 400:
          alert(error.response.data.message); // "No file provided" or "Invalid file type"
          break;
        case 401:
          alert('Please login first');
          break;
        case 403:
          alert('Admin access required');
          break;
        default:
          alert('Upload failed. Please try again.');
      }
    } else {
      alert('Network error. Please check your connection.');
    }
    throw error;
  }
};
```

---

## Testing with cURL

```bash
# Upload file
curl -X POST http://localhost:5000/api/upload/document \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@/path/to/document.pdf"

# Delete file
curl -X DELETE http://localhost:5000/api/upload/document/filename.pdf \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## Testing with Postman

1. **Create new request**: `POST http://localhost:5000/api/upload/document`
2. **Headers**:
   - `Authorization: Bearer {your_token}`
3. **Body**:
   - Select `form-data`
   - Key: `file` (change type to `File`)
   - Value: Select your PDF/Word file
4. **Send**

---

## Storage Location

Files are stored in:
```
/uploads/documents/
```

File naming format:
```
{uuid}_{timestamp}.{extension}
```

Example:
```
abc123def456_20251217_110530.pdf
```

---

## Security Notes

- ✅ Only admin can upload files
- ✅ File extension validation
- ✅ Secure filename generation
- ✅ Unique filenames prevent overwriting
- ✅ File size limit enforced
- ⚠️ Consider adding virus scanning in production
- ⚠️ Consider using cloud storage (S3, GCS) for production
