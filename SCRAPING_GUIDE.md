# Web Scraping Guide - Mauvanban.vn

## 🕷️ Crawl Dữ Liệu Từ Mauvanban.vn

Script này sẽ crawl categories và documents từ website mauvanban.vn.

---

## Cài Đặt Dependencies

```bash
pip install beautifulsoup4 requests lxml
```

Hoặc:

```bash
pip install -r requirements.txt
```

---

## Chạy Script Crawl

```bash
python scripts/crawl_mauvanban.py
```

---

## Script Sẽ Làm Gì?

1. ✅ Crawl danh sách categories từ trang chủ
2. ✅ Crawl documents từ mỗi category (giới hạn 5 docs/category)
3. ✅ Crawl chi tiết mỗi document (title, description, content, guide)
4. ✅ Lưu vào file JSON: `scripts/crawled_data.json`
5. ✅ Tự động import vào database

---

## Lưu Ý Quan Trọng

### ⚠️ Selectors Cần Điều Chỉnh

Script hiện tại sử dụng **selectors giả định**. Bạn cần inspect website thực tế và sửa lại:

```python
# Trong hàm crawl_categories()
category_links = soup.find_all('a', class_='category-link')  # ← Sửa class này

# Trong hàm crawl_documents()
doc_items = soup.find_all('div', class_='document-item')  # ← Sửa class này

# Trong hàm crawl_document_detail()
description_elem = soup.find('div', class_='description')  # ← Sửa class này
content_elem = soup.find('div', class_='content')  # ← Sửa class này
```

### 🔍 Cách Tìm Selectors Đúng

1. **Mở mauvanban.vn** trong Chrome
2. **Right-click** vào element → **Inspect**
3. **Xem HTML structure** và class names
4. **Sửa lại selectors** trong script

**Ví dụ:**

Nếu HTML thực tế là:
```html
<div class="category-menu">
  <a href="/hop-dong" class="cat-link">Hợp đồng</a>
</div>
```

Thì sửa thành:
```python
category_links = soup.find_all('a', class_='cat-link')
```

---

## Fallback Data

Nếu crawling thất bại (do selectors sai hoặc website block), script sẽ dùng **fallback data**:

```python
categories = [
    {'name': 'Hợp đồng', 'url': f'{BASE_URL}/hop-dong', 'slug': 'hop-dong'},
    {'name': 'Đơn từ', 'url': f'{BASE_URL}/don-tu', 'slug': 'don-tu'},
    {'name': 'Biên bản', 'url': f'{BASE_URL}/bien-ban', 'slug': 'bien-ban'},
    {'name': 'Giấy ủy quyền', 'url': f'{BASE_URL}/giay-uy-quyen', 'slug': 'giay-uy-quyen'},
]
```

---

## Tùy Chỉnh

### Giới hạn số lượng

```python
# Trong main()
for category in categories[:5]:  # ← Crawl 5 categories đầu
    docs = crawl_documents(category['url'], category['name'], limit=5)  # ← 5 docs/category
```

### Delay giữa requests

```python
time.sleep(1)  # ← Tăng lên 2-3 giây nếu bị block
```

---

## Output

### File JSON

```json
[
  {
    "name": "Hợp đồng",
    "slug": "hop-dong",
    "url": "https://mauvanban.vn/hop-dong",
    "documents": [
      {
        "title": "Hợp đồng thuê nhà",
        "description": "Mẫu hợp đồng...",
        "content": "CỘNG HÒA...",
        "url": "https://mauvanban.vn/hop-dong/thue-nha",
        "guide": {
          "usage_guide": "Sử dụng khi...",
          "filling_guide": "Điền đầy đủ..."
        }
      }
    ]
  }
]
```

### Database

Tự động tạo:
- Categories với slug
- Documents với code tự động (VD: HOP-001, HOP-002)
- DocumentGuides với thông tin hướng dẫn

---

## Troubleshooting

### Lỗi: No categories found

**Nguyên nhân:** Selectors không đúng

**Giải pháp:**
1. Inspect website
2. Sửa selectors trong `crawl_categories()`
3. Hoặc dùng fallback data

### Lỗi: Connection timeout

**Nguyên nhân:** Website chậm hoặc block

**Giải pháp:**
```python
response = requests.get(url, timeout=30)  # Tăng timeout
time.sleep(3)  # Tăng delay
```

### Lỗi: 403 Forbidden

**Nguyên nhân:** Website block bot

**Giải pháp:**
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
response = requests.get(url, headers=headers)
```

---

## Alternative: Manual Data Entry

Nếu crawling không hoạt động, bạn có thể:

1. **Dùng seed script** có sẵn:
```bash
python scripts/seed_data.py
```

2. **Tạo thủ công qua Swagger UI**:
- Categories: `POST /api/admin/categories`
- Documents: `POST /api/admin/documents/json`

3. **Import từ CSV**:
Tạo file CSV và viết script import

---

## Best Practices

- ✅ Respect robots.txt
- ✅ Add delays between requests (1-2 seconds)
- ✅ Use proper User-Agent
- ✅ Don't overload the server
- ✅ Cache results to avoid re-crawling
- ⚠️ Check website's Terms of Service

---

## Next Steps

1. **Chạy script** và xem kết quả
2. **Kiểm tra** `crawled_data.json`
3. **Verify** data trong database
4. **Adjust selectors** nếu cần
5. **Run again** để crawl thêm data

---

## Support

Nếu gặp vấn đề:
1. Check console output để xem lỗi
2. Inspect website HTML structure
3. Adjust selectors accordingly
4. Use fallback data if needed
