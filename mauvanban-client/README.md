# Mẫu Văn Bản - Frontend Client

React + TypeScript + Tailwind CSS frontend cho hệ thống quản lý văn bản.

## 🚀 Setup

### Prerequisites

- Node.js 18+ và npm
- Backend API đang chạy tại `http://localhost:5000`

### Installation

```bash
# Di chuyển vào thư mục frontend
cd mauvanban-client

# Cài đặt dependencies
npm install

# Chạy development server
npm run dev
```

Frontend sẽ chạy tại: **http://localhost:3000**

---

## 📁 Project Structure

```
mauvanban-client/
├── src/
│   ├── api/              # API client & endpoints
│   │   ├── axios.ts      # Axios instance với interceptors
│   │   └── auth.ts       # Authentication API
│   ├── components/       # React components
│   │   └── layout/       # Header, Footer
│   ├── pages/            # Page components
│   │   ├── Home.tsx
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Documents.tsx
│   │   └── DocumentDetail.tsx
│   ├── store/            # Zustand state management
│   │   └── authStore.ts  # Authentication state
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

---

## 🔑 Features Implemented

### ✅ Core Features
- React 18 với TypeScript
- Vite build tool
- Tailwind CSS styling
- React Router v6
- Zustand state management
- React Query (ready to use)

### ✅ Authentication
- Login/Logout
- JWT token management
- Auto token refresh
- Protected routes (ready)

### ✅ UI Components
- Responsive Header với navigation
- Footer
- Home page với hero section
- Login page với form validation

---

## 🎨 Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Routing
- **Zustand** - State management
- **Axios** - HTTP client
- **React Query** - Server state

---

## 🔧 Configuration

### Environment Variables

Tạo file `.env` trong thư mục `mauvanban-client`:

```env
VITE_API_URL=http://localhost:5000/api
```

---

## 📝 Usage

### Login

1. Mở http://localhost:3000/login
2. Nhập credentials:
   - Email: `admin@mauvanban.vn`
   - Password: `Admin@123`
3. Click "Đăng nhập"

### API Integration

API client đã được setup với:
- Auto token injection
- Token refresh on 401
- Error handling

```typescript
// Example usage
import api from '@/api/axios';

const response = await api.get('/documents');
```

---

## 🚧 Next Steps

### Pages to Implement:
- [ ] Register page (form đầy đủ)
- [ ] Documents list với pagination
- [ ] Document detail với purchase
- [ ] Profile page
- [ ] My Documents page
- [ ] Admin dashboard

### Components to Build:
- [ ] DocumentCard component
- [ ] CategoryFilter component
- [ ] SearchBar component
- [ ] Modal component
- [ ] Loading states
- [ ] Error boundaries

---

## 🎯 Development Workflow

1. **Start backend**: `python main.py` (port 5000)
2. **Start frontend**: `npm run dev` (port 3000)
3. **Open browser**: http://localhost:3000

---

## 📚 Documentation

- [React Docs](https://react.dev/)
- [TypeScript Docs](https://www.typescriptlang.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Vite Guide](https://vitejs.dev/)
- [Zustand](https://github.com/pmndrs/zustand)

---

## 🐛 Troubleshooting

### Port already in use
```bash
# Kill process on port 3000
npx kill-port 3000
```

### CORS errors
- Đảm bảo backend có CORS enabled
- Check `vite.config.ts` proxy settings

### API connection failed
- Verify backend đang chạy
- Check `VITE_API_URL` trong `.env`

---

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit PR

---

## 📄 License

MIT
