import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { Bars3Icon, XMarkIcon, MagnifyingGlassIcon, UserCircleIcon } from '@heroicons/react/24/outline';

export default function Header() {
    const { user, isAuthenticated, logout } = useAuthStore();
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    return (
        <header className="bg-white shadow-sm sticky top-0 z-50">
            {/* Top Bar - Hidden on Mobile */}
            <div className="bg-primary-900 text-white text-xs py-1 px-4 hidden md:block">
                <div className="max-w-7xl mx-auto flex justify-between">
                    <span>Hotline: 0398.481.719 | Email: hotro@mauvanban.vn</span>
                    <span>Cập nhật hàng nghìn biểu mẫu mới mỗi ngày!</span>
                </div>
            </div>

            <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-20">
                    {/* Logo */}
                    <div className="flex items-center">
                        <Link to="/" className="flex items-center gap-2 group">
                            <div className="bg-primary-600 text-white p-2 rounded-lg group-hover:bg-primary-700 transition">
                                <span className="text-2xl font-bold">MVB</span>
                            </div>
                            <div className="flex flex-col">
                                <span className="text-xl font-bold text-primary-900 leading-none">Mẫu Văn Bản</span>
                                <span className="text-[10px] md:text-xs text-gray-500 uppercase tracking-wider">Chuyên nghiệp & Chính xác</span>
                            </div>
                        </Link>
                    </div>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center gap-8">
                        <div className="flex space-x-1">
                            <Link to="/documents" className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50">
                                Tất cả văn bản
                            </Link>
                            <Link to="/categories" className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50">
                                Danh mục
                            </Link>
                            <Link to="/contact" className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50">
                                Liên hệ
                            </Link>
                            <Link to="/news" className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50">
                                Tin tức
                            </Link>
                        </div>

                        {isAuthenticated ? (
                            <div className="flex items-center gap-4">
                                <div className="flex flex-col items-end mr-2">
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
                                        <Link to="/profile" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Hồ sơ cá nhân</Link>
                                        <Link to="/my-documents" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Văn bản của tôi</Link>
                                        {user?.role === 'admin' && (
                                            <Link to="/admin" className="block px-4 py-2 text-sm text-red-600 hover:bg-red-50 font-medium">Trang quản trị</Link>
                                        )}
                                        <button onClick={logout} className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Đăng xuất</button>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="flex items-center gap-3">
                                <Link to="/login" className="text-gray-700 hover:text-primary-600 font-medium text-sm">Đăng nhập</Link>
                                <Link to="/register" className="bg-secondary-500 hover:bg-secondary-600 text-white px-4 py-2 rounded-full font-medium text-sm transition shadow-md">
                                    Đăng ký
                                </Link>
                            </div>
                        )}
                    </div>

                    {/* Mobile Controls */}
                    <div className="flex md:hidden items-center gap-2">
                        <Link to="/documents" className="p-2 text-gray-500">
                            <MagnifyingGlassIcon className="w-6 h-6" />
                        </Link>

                        <button
                            onClick={() => setIsMenuOpen(!isMenuOpen)}
                            className="p-2 text-gray-500 hover:bg-gray-100 rounded-md transition"
                        >
                            {isMenuOpen ? <XMarkIcon className="w-7 h-7" /> : <Bars3Icon className="w-7 h-7" />}
                        </button>
                    </div>
                </div>
            </nav>

            {/* Mobile Menu Backdrop */}
            {isMenuOpen && (
                <div
                    className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
                    onClick={() => setIsMenuOpen(false)}
                ></div>
            )}

            {/* Mobile Menu Drawer */}
            <div className={`fixed top-0 right-0 h-full w-72 bg-white z-50 transform transition-transform duration-300 ease-in-out md:hidden ${isMenuOpen ? 'translate-x-0' : 'translate-x-full'}`}>
                <div className="p-6">
                    <div className="flex justify-between items-center mb-8">
                        <span className="text-xl font-bold text-primary-900">Menu</span>
                        <button onClick={() => setIsMenuOpen(false)}><XMarkIcon className="w-6 h-6 text-gray-500" /></button>
                    </div>

                    {isAuthenticated && (
                        <div className="mb-8 p-4 bg-gray-50 rounded-xl flex items-center gap-3">
                            <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center text-primary-700 font-bold">
                                {user?.email?.charAt(0).toUpperCase()}
                            </div>
                            <div>
                                <p className="text-sm font-bold text-gray-900 truncate max-w-[150px]">{user?.full_name || user?.email}</p>
                                <p className="text-xs text-primary-600 font-bold">{user?.balance?.toLocaleString()}đ</p>
                            </div>
                        </div>
                    )}

                    <div className="flex flex-col gap-4">
                        <Link to="/documents" onClick={() => setIsMenuOpen(false)} className="flex items-center gap-3 text-gray-700 font-medium p-2 hover:bg-primary-50 hover:text-primary-600 rounded-lg transition">
                            <Bars3Icon className="w-5 h-5" /> Tất cả văn bản
                        </Link>
                        <Link to="/categories" onClick={() => setIsMenuOpen(false)} className="flex items-center gap-3 text-gray-700 font-medium p-2 hover:bg-primary-50 hover:text-primary-600 rounded-lg transition">
                            <Bars3Icon className="w-5 h-5" /> Danh mục
                        </Link>
                        <Link to="/contact" onClick={() => setIsMenuOpen(false)} className="flex items-center gap-3 text-gray-700 font-medium p-2 hover:bg-primary-50 hover:text-primary-600 rounded-lg transition">
                            <Bars3Icon className="w-5 h-5" /> Liên hệ
                        </Link>
                        <Link to="/news" onClick={() => setIsMenuOpen(false)} className="flex items-center gap-3 text-gray-700 font-medium p-2 hover:bg-primary-50 hover:text-primary-600 rounded-lg transition">
                            <Bars3Icon className="w-5 h-5" /> Tin tức
                        </Link>

                        <hr className="my-2 border-gray-100" />

                        {isAuthenticated ? (
                            <>
                                <Link to="/profile" onClick={() => setIsMenuOpen(false)} className="flex items-center gap-3 text-gray-700 font-medium p-2 hover:bg-primary-50 hover:text-primary-600 rounded-lg transition">
                                    Hồ sơ cá nhân
                                </Link>
                                <Link to="/my-documents" onClick={() => setIsMenuOpen(false)} className="flex items-center gap-3 text-gray-700 font-medium p-2 hover:bg-primary-50 hover:text-primary-600 rounded-lg transition">
                                    Văn bản của tôi
                                </Link>
                                <button
                                    onClick={() => { logout(); setIsMenuOpen(false); }}
                                    className="flex items-center gap-3 text-red-600 font-medium p-2 hover:bg-red-50 rounded-lg transition text-left"
                                >
                                    Đăng xuất
                                </button>
                            </>
                        ) : (
                            <div className="flex flex-col gap-3 pt-4">
                                <Link to="/login" onClick={() => setIsMenuOpen(false)} className="btn btn-secondary text-center">Đăng nhập</Link>
                                <Link to="/register" onClick={() => setIsMenuOpen(false)} className="btn bg-primary-600 text-white text-center">Đăng ký ngay</Link>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </header>
    );
}
