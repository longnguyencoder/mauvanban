import { useQuery } from '@tanstack/react-query';
import api from '../../api/axios';

export default function Dashboard() {
    const { data, isLoading } = useQuery({
        queryKey: ['admin-stats'],
        queryFn: () => api.get('/admin/stats'),
    });

    const stats = data?.data?.data || {};

    if (isLoading) return <div>Đang tải dữ liệu thống kê...</div>;

    return (
        <div>
            <h2 className="text-2xl font-bold mb-6">Tổng quan hệ thống</h2>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                {[
                    {
                        label: 'Tổng văn bản',
                        value: stats.total_documents?.toLocaleString() || '0',
                        color: 'bg-blue-500',
                        icon: '📄'
                    },
                    {
                        label: 'Người dùng',
                        value: stats.total_users?.toLocaleString() || '0',
                        color: 'bg-green-500',
                        icon: '👥'
                    },
                    {
                        label: 'Doanh thu (Nạp)',
                        value: `${(stats.total_revenue || 0).toLocaleString()}đ`,
                        color: 'bg-purple-500',
                        icon: '💰'
                    },
                    {
                        label: 'Tổng lượt tải',
                        value: stats.total_downloads?.toLocaleString() || '0',
                        color: 'bg-orange-500',
                        icon: '⬇️'
                    },
                ].map((stat, idx) => (
                    <div key={idx} className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 flex items-center">
                        <div className={`w-12 h-12 rounded-full ${stat.color} bg-opacity-10 flex items-center justify-center mr-4 text-2xl`}>
                            {stat.icon}
                        </div>
                        <div>
                            <p className="text-gray-500 text-sm">{stat.label}</p>
                            <p className="text-2xl font-bold text-gray-800">{stat.value}</p>
                        </div>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white rounded-lg shadow-sm p-6">
                    <h3 className="font-bold mb-4">Hoạt động hôm nay</h3>
                    <ul className="space-y-3">
                        <li className="flex justify-between border-b pb-2">
                            <span>Người dùng mới đăng ký</span>
                            <span className="font-bold">{stats.new_users_today || 0}</span>
                        </li>
                        <li className="flex justify-between border-b pb-2">
                            <span>Tổng lượt xem toàn trang</span>
                            <span className="font-bold">{stats.total_views?.toLocaleString() || 0}</span>
                        </li>
                    </ul>
                </div>

                <div className="bg-white rounded-lg shadow-sm p-6 flex items-center justify-center text-gray-400">
                    (Biểu đồ tăng trưởng sẽ cập nhật sau)
                </div>
            </div>
        </div>
    );
}
