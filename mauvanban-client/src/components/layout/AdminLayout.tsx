import { Link, Outlet, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

export default function AdminLayout() {
    const { user, logout } = useAuthStore();
    const location = useLocation();

    if (!user || user.role !== 'admin') {
        return <div className="p-8 text-center text-red-600">Bạn không có quyền truy cập trang này.</div>;
    }

    const menuItems = [
        { title: 'Tổng quan', path: '/admin', icon: '📊' },
        { title: 'Quản lý Văn bản', path: '/admin/documents', icon: '📄' },
        { title: 'Danh mục', path: '/admin/categories', icon: '📂' },
        { title: 'Người dùng', path: '/admin/users', icon: '👥' },
        { title: 'Gói dịch vụ', path: '/admin/packages', icon: '📦' },
        { title: 'Tiền tệ & GD', path: '/admin/transactions', icon: '💰' },
    ];

    return (
        <div className="min-h-screen bg-gray-100 flex">
            {/* Sidebar */}
            <aside className="w-64 bg-gray-900 text-white flex flex-col flex-shrink-0">
                <div className="p-6 border-b border-gray-800">
                    <h1 className="text-2xl font-bold text-white">Admin Portal</h1>
                    <p className="text-gray-400 text-sm mt-1">Quản lý hệ thống</p>
                </div>

                <nav className="flex-1 overflow-y-auto py-4">
                    <ul className="space-y-1">
                        {menuItems.map((item) => (
                            <li key={item.path}>
                                <Link
                                    to={item.path}
                                    className={`flex items-center gap-3 px-6 py-3 text-sm font-medium transition-colors ${location.pathname === item.path || (item.path !== '/admin' && location.pathname.startsWith(item.path))
                                            ? 'bg-primary-600 text-white'
                                            : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                                        }`}
                                >
                                    <span className="text-xl">{item.icon}</span>
                                    {item.title}
                                </Link>
                            </li>
                        ))}
                    </ul>
                </nav>

                <div className="p-4 border-t border-gray-800">
                    <div className="flex items-center gap-3 mb-4 px-2">
                        <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center font-bold">
                            {user.email.charAt(0).toUpperCase()}
                        </div>
                        <div className="overflow-hidden">
                            <p className="text-sm font-medium truncate">{user.full_name}</p>
                            <p className="text-xs text-gray-500 truncate">{user.email}</p>
                        </div>
                    </div>
                    <button
                        onClick={logout}
                        className="w-full btn bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm"
                    >
                        Đăng xuất
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto p-8">
                <Outlet />
            </main>
        </div>
    );
}
