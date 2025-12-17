import { Link } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

export default function Header() {
    const { user, isAuthenticated, logout } = useAuthStore();

    return (
        <header className="bg-white shadow-sm sticky top-0 z-50">
            {/* Top Bar (Optional - for contact info) */}
            <div className="bg-primary-900 text-white text-xs py-1 px-4 hidden md:block">
                <div className="max-w-7xl mx-auto flex justify-between">
                    <span>Hotline: 0398.481.719 | Email: hotro@mauvanban.vn</span>
                    <span>Cập nhật hàng nghìn biểu mẫu mới mỗi ngày!</span>
                </div>
            </div>

            <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-20">
                    {/* Logo & Main Nav */}
                    <div className="flex items-center gap-8">
                        <Link to="/" className="flex items-center gap-2 group">
                            <div className="bg-primary-600 text-white p-2 rounded-lg group-hover:bg-primary-700 transition">
                                <span className="text-2xl font-bold">MVB</span>
                            </div>
                            <div className="flex flex-col">
                                <span className="text-xl font-bold text-primary-900 leading-none">Mẫu Văn Bản</span>
                                <span className="text-xs text-gray-500 uppercase tracking-wider">Chuyên nghiệp & Chính xác</span>
                            </div>
                        </Link>

                        <div className="hidden md:flex space-x-1">
                            <Link to="/documents" className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50">
                                Tất cả văn bản
                            </Link>
                            <Link to="/categories" className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50">
                                Danh mục
                            </Link>
                            <a href="#" className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50">
                                Tin tức
                            </a>
                            <Link to="/contact" className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50">
                                Liên hệ
                            </Link>
                        </div>
                    </div>

                    {/* User & Actions */}
                    <div className="flex items-center gap-4">
                        {/* Search Icon (Mobile) */}
                        <button className="md:hidden text-gray-500">
                            <span className="text-xl">🔍</span>
                        </button>

                        {isAuthenticated ? (
                            <div className="flex items-center gap-4">
                                <div className="hidden md:flex flex-col items-end mr-2">
                                    <span className="text-xs text-gray-500">Số dư</span>
                                    <span className="text-sm font-bold text-secondary-600">{user?.balance?.toLocaleString()}đ</span>
                                </div>

                                <div className="relative group">
                                    <button className="flex items-center gap-2 focus:outline-none">
                                        <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center text-primary-700 font-bold border border-primary-200">
                                            {user?.email?.charAt(0).toUpperCase()}
                                        </div>
                                    </button>
                                    {/* Dropdown Menu */}
                                    <div className="absolute right-0 mt-1 w-56 bg-white rounded-md shadow-lg py-1 ring-1 ring-black ring-opacity-5 hidden group-hover:block hover:block before:absolute before:-top-2 before:left-0 before:w-full before:h-4 before:bg-transparent">
                                        <div className="px-4 py-2 border-b">
                                            <p className="text-sm truncate font-medium text-gray-900">{user?.full_name || 'User'}</p>
                                            <p className="text-xs truncate text-gray-500">{user?.email}</p>
                                        </div>
                                        <Link to="/profile" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                                            Hồ sơ cá nhân
                                        </Link>
                                        <Link to="/my-documents" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                                            Văn bản của tôi
                                        </Link>
                                        {user?.role === 'admin' && (
                                            <Link to="/admin" className="block px-4 py-2 text-sm text-red-600 hover:bg-red-50 font-medium">
                                                Trang quản trị
                                            </Link>
                                        )}
                                        <button
                                            onClick={logout}
                                            className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                        >
                                            Đăng xuất
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="flex items-center gap-3">
                                <Link to="/login" className="text-gray-700 hover:text-primary-600 font-medium text-sm">
                                    Đăng nhập
                                </Link>
                                <Link
                                    to="/register"
                                    className="bg-secondary-500 hover:bg-secondary-600 text-white px-4 py-2 rounded-full font-medium text-sm transition shadow-md"
                                >
                                    Đăng ký ngay
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            </nav>
        </header>
    );
}
