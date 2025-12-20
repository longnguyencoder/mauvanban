# Hướng Dẫn Cấu Hình VPS & Deploy (Toàn Tập)

Tài liệu này chứa **tất cả** những gì bạn cần để chạy website trên VPS (Production).

## 1. Cấu hình Backend (.env)

Trên VPS, mở file `.env` trong thư mục `backend` và sửa các dòng sau:

```ini
# --- Môi trường ---
FLASK_ENV=production
PORT=8001

# --- Thư mục Upload (BẮT BUỘC SỬA) ---
# Dùng đường dẫn tuyệt đối. Ví dụ:
UPLOAD_FOLDER=/var/www/mauvanban/uploads

# --- Domain & CORS (Quan trọng) ---
# Cho phép domain của bạn và dashboard admin gọi API
CORS_ORIGINS=https://mauvanban.zluat.vn,https://admin.mauvanban.zluat.vn

# --- Cấu hình SePay (Thanh toán) ---
SEPAY_API_KEY=xxx
SEPAY_ACCOUNT_ID=xxx
SEPAY_SECRET_KEY=xxx
SEPAY_BANK_ACCOUNT=xxx
SEPAY_BANK_NAME=xxx
SEPAY_ENABLED=True
```

## 2. Cấu hình Frontend (Build React App)

Khi build frontend để up lên VPS, bạn phải chỉ định URL của API backend.

**Cách 1: Tạo file `.env.production` trong thư mục `mauvanban-client`**
```ini
VITE_API_URL=https://mauvanban.zluat.vn
```

**Cách 2: Build trực tiếp với biến môi trường**
Chạy lệnh này trên máy local của bạn trước khi copy folder `dist` lên VPS:
```bash
# Windows (Powershell)
$env:VITE_API_URL="https://mauvanban.zluat.vn"; npm run build

# Linux/Mac
VITE_API_URL=https://mauvanban.zluat.vn npm run build
```

### Cơ chế hoạt động (Tại sao config như vậy là đúng?)

Bạn đang cấu hình **VITE_API_URL=https://mauvanban.zluat.vn** là **CHÍNH XÁC 100%**.

**Mô hình luồng đi của dữ liệu:**

```mermaid
graph LR
    User[Người dùng / Trình duyệt] -- 1. Gọi HTTPS --> Cloudflare[Internet / Cloudflare]
    Cloudflare -- 2. Vào cổng 443 --> Nginx[Nginx (Public)]
    Nginx -- 3. Proxy Pass (Nội bộ) --> Backend[Backend Python (Port 8001)]
```

**Giải thích:**
1.  **Người dùng (Client)**: Chỉ nhìn thấy và truy cập được vào domain công khai `https://mauvanban.zluat.vn`. Họ **không thể** truy cập trực tiếp vào `127.0.0.1:8001` của bạn (vì đó là IP nội bộ của server, không phải của họ).
2.  **Frontend (React)**: Chạy trên trình duyệt của người dùng. Nên nó phải gọi API vào domain công khai.
3.  **Nginx**: Đứng ở cửa ngõ, nhận yêu cầu từ domain công khai, sau đó âm thầm chuyển (proxy) yêu cầu đó vào trong cho Backend ở cổng 8001 xử lý.

=> Nếu bạn cấu hình Frontend trỏ vào `127.0.0.1:8001`, trình duyệt của khách sẽ cố kết nối vào... máy tính của chính họ (localhost) và sẽ báo lỗi không kết nối được.

Sau đó copy thư mục `dist` lên VPS.

## 3. Cấu hình SePay (Dashboard)

Để thanh toán hoạt động, SePay cần biết "gọi lại" (webhook) vào đâu khi khách chuyển tiền xong.

1. Truy cập [my.sepay.vn](https://my.sepay.vn)
2. Vào mục **Cấu hình tích hợp** (Webhook).
3. Điền **Webhook URL**:
   ```
   https://mauvanban.zluat.vn/api/sepay/webhook
   ```
   *(Thay domain của bạn vào)*
4. Lưu lại.

## 4. Cấu hình Nginx (Đầy đủ)

File: `/etc/nginx/sites-available/mauvanban.zluat.vn`

```nginx
server {
    server_name mauvanban.zluat.vn;

    root /var/www/mauvanban/frontend; # Trỏ vào folder 'dist' của frontend
    index index.html;

    # 1. Phục vụ Frontend (React)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 2. Proxy cho Backend API
    location /api {
        proxy_pass http://127.0.0.1:8001; # Backend chạy port 8001
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 3. Phục vụ File/Ảnh Upload (QUAN TRỌNG)
    location /uploads/documents/ {
        # Phải KHỚP với UPLOAD_FOLDER trong backend/.env
        alias /home/zluat-mauvanban/htdocs/mauvanban.zluat.vn/backend/uploads/documents/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
```

## 4b. Cấu hình trên CloudPanel (Nếu dùng CloudPanel)
Nếu bạn dùng CloudPanel:
1. Vào **Sites > Manage > Vhost**.
2. Tìm trong file cấu hình (nó tương tự như trên), chèn đoạn code sau vào trong block `server { ... }`:

```nginx
    # 2. Proxy cho Backend API
    location /api {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 3. Phục vụ File/Ảnh Upload (QUAN TRỌNG)
    # Thêm dấu ^~ để bắt buộc Nginx chọn block này thay vì block mặc định của CloudPanel
    location ^~ /uploads/documents/ {
        # ĐƯỜNG DẪN CHÍNH XÁC
        alias /home/zluat-mauvanban/htdocs/mauvanban.zluat.vn/backend/uploads/documents/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
```
3. Bấm **Save** để CloudPanel tự restart Nginx.

## 5. Các lỗi thường gặp

### ❌ Lỗi 400 Bad Request khi thêm văn bản
- Nguyên nhân: Giá tiền quá lớn (> 100 triệu).
- Khắc phục: Chạy lệnh update DB trên VPS:
  ```bash
  source venv/bin/activate
  python backend/scripts/update_price_precision.py
  ```

### ❌ Lỗi ảnh không hiện (404 Not Found)
- Nguyên nhân: Nginx config sai `alias` hoặc chưa cấp quyền thư mục.
- Khắc phục:
  - Xem lại mục 4 ở trên.
  - Chạy `sudo chown -R www-data:www-data /var/www/mauvanban/uploads`
  - Chạy `sudo systemctl restart nginx`

### ❌ Lỗi Trắng Trang (Blank Page) / 404 khi load lại trang
- **Nguyên nhân 1: Chưa cấu hình Nginx cho SPA (Single Page App)**
  - Kiểm tra file config Nginx xem có dòng `try_files $uri $uri/ /index.html;` chưa.
  - Dòng này cực kỳ quan trọng để React Router hoạt động.
- **Nguyên nhân 2: Code cũ bị cache**
  - Thử mở tab ẩn danh (Incognito) xem có lên không.
  - Nếu lên -> Xóa cache trình duyệt.
- **Nguyên nhân 3: Sai đường dẫn API**
  - Kiểm tra Console (F12 > Console). Nếu thấy lỗi đỏ `Failed to load resource: net::ERR_CONNECTION_REFUSED` -> Backend chưa chạy hoặc URL API sai.
  - Build lại frontend với đúng biến môi trường `VITE_API_URL`.

### ❌ Lỗi 500 Internal Server Error (Quan trọng)
Đây là lỗi Backend bị crash. Để biết chính xác lỗi gì, bạn CẦN PHẢI xem log báo lỗi trên VPS.

**Cách xem log lỗi:**
Chạy lệnh này trên VPS để xem backend đang "kêu khóc" điều gì:
```bash
# Xem 50 dòng log cuối cùng (realtime)
sudo journalctl -u mauvanban-backend -f
```
Sau đó bạn thử load lại web để xem dòng lỗi đỏ hiện ra là gì (ví dụ: `ImportError`, `DatabaseError`, `KeyError`...). Chụp ảnh lỗi đó gửi cho tôi để tôi chỉ cách sửa.

### ❌ Lỗi Database: Connection refused
Lỗi: `sqlalchemy.exc.OperationalError: ... connection to server ... failed: Connection refused`

**Nguyên nhân**: Dịch vụ PostgreSQL trên VPS chưa chạy hoặc bị tắt.

**Khắc phục**:
1.  Kiểm tra trạng thái: `sudo systemctl status postgresql`
2.  Khởi động lại nó: `sudo systemctl restart postgresql`
3.  Nếu chưa có PostgreSQL (quên cài):
    ```bash
    sudo apt update
    sudo apt install postgresql postgresql-contrib
    ```
4.  Sau khi start DB xong, nhớ restart lại backend: `sudo systemctl restart mauvanban-backend`

### ❌ Kiểm tra nhanh kết nối Database
Để biết chắc chắn Database có thông hay không, bạn chạy script này trên VPS:
```bash
python backend/scripts/check_db_connection.py
```
Nếu nó báo `SUCCESS`, lỗi 500 do nguyên nhân khác. Nếu báo `FAILED`, nó sẽ in ra lý do cụ thể.

### ❌ Lỗi SePay không cập nhật thanh toán
- Kiểm tra 3 thứ:
  1. Webhook URL trên SePay dashboard đúng chưa?
  2. `SEPAY_SECRET_KEY` trong `.env` backend có trùng với trên SePay không?
  3. Server backend có đang chạy không?

## 6. Tổng kết: Sau khi sửa xong thì làm gì?

Tùy vào bạn sửa cái gì mà hành động sẽ khác nhau:

| Bạn vừa sửa cái gì? | Có cần Build lại? | Lệnh cần chạy |
| :--- | :--- | :--- |
| **Sửa Backend** (Python code, .env) | **KHÔNG** | `sudo systemctl restart mauvanban-backend` |
| **Sửa Nginx** (Đổi port, proxy) | **KHÔNG** | `sudo systemctl restart nginx` |
| **Sửa Frontend** (HTML, CSS, JS) | **CÓ** (Local) | Build lại ở local -> Copy folder `dist` lên |

**Trường hợp của bạn (Đổi port 8001):**
Chỉ cần restart Backend và Nginx. **Không** cần động vào Frontend.
