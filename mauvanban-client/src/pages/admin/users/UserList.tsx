import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { usersApi, User } from '../../../api/users';

export default function UserList() {
    const [page, setPage] = useState(1);
    const queryClient = useQueryClient();

    const { data, isLoading } = useQuery({
        queryKey: ['admin-users', page],
        queryFn: () => usersApi.getAll({ page, per_page: 10 }),
    });

    const toggleActiveMutation = useMutation({
        mutationFn: (id: string) => usersApi.toggleActive(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-users'] });
        },
        onError: (err: any) => alert('Lỗi: ' + (err?.response?.data?.message || err.message))
    });

    const deleteMutation = useMutation({
        mutationFn: (id: string) => usersApi.delete(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-users'] });
            alert('Xóa người dùng thành công!');
        },
        onError: (err: any) => alert('Lỗi xóa: ' + (err?.response?.data?.message || err.message))
    });

    const handleDelete = (id: string) => {
        if (window.confirm('CẢNH BÁO: Xóa người dùng sẽ xóa toàn bộ dữ liệu liên quan (giao dịch, văn bản đã lưu...). Bạn có chắc chắn không?')) {
            deleteMutation.mutate(id);
        }
    };

    const handleToggleActive = (id: string) => {
        toggleActiveMutation.mutate(id);
    };

    const handleAdjustBalance = async (user: User) => {
        const amountStr = prompt(`Điều chỉnh số dư cho ${user.full_name}\nNhập số tiền (dương để cộng, âm để trừ):`, '0');
        if (amountStr) {
            const amount = parseFloat(amountStr);
            if (!isNaN(amount) && amount !== 0) {
                try {
                    await usersApi.adjustBalance(user.id, amount);
                    queryClient.invalidateQueries({ queryKey: ['admin-users'] });
                    alert('Cập nhật số dư thành công!');
                } catch (err: any) {
                    alert('Lỗi: ' + (err?.response?.data?.message || err.message));
                }
            }
        }
    };

    if (isLoading) return <div>Đang tải...</div>;

    const users = data?.data?.data?.users || [];
    const meta = data?.data?.data;

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">Quản lý Người dùng</h2>
                <Link to="/admin/users/create" className="btn btn-primary">
                    + Thêm người dùng mới
                </Link>
            </div>

            <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Thông tin</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Liên hệ</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vai trò</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Số dư</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trạng thái</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Thao tác</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {users.map((user: User) => (
                            <tr key={user.id} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm font-medium text-gray-900">{user.full_name || 'Chưa đặt tên'}</div>
                                    <div className="text-xs text-gray-400">ID: {user.id.substring(0, 8)}...</div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-gray-900">{user.email}</div>
                                    <div className="text-xs text-gray-500">{user.phone_number || '---'}</div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    <span className={`px-2 py-1 rounded-full text-xs font-bold ${user.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'}`}>
                                        {user.role}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">
                                    {user.balance?.toLocaleString()}đ
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                    <button
                                        onClick={() => handleToggleActive(user.id)}
                                        className={`px-2 py-1 rounded-full text-xs font-bold cursor-pointer hover:opacity-80 transition ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}
                                    >
                                        {user.is_active ? 'Hoạt động' : 'Bị khóa'}
                                    </button>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <button
                                        onClick={() => handleAdjustBalance(user)}
                                        className="text-yellow-600 hover:text-yellow-900 mr-3"
                                        title="Nạp/Trừ tiền"
                                    >
                                        💰
                                    </button>
                                    <Link
                                        to={`/admin/users/edit/${user.id}`}
                                        className="text-primary-600 hover:text-primary-900 mr-3"
                                    >
                                        Sửa
                                    </Link>
                                    {user.role !== 'admin' && (
                                        <button
                                            onClick={() => handleDelete(user.id)}
                                            className="text-red-600 hover:text-red-900"
                                        >
                                            Xóa
                                        </button>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {(meta?.pages || 0) > 1 && (
                <div className="mt-4 flex justify-end gap-2">
                    <button
                        disabled={page === 1}
                        onClick={() => setPage(p => p - 1)}
                        className="btn btn-secondary text-sm disabled:opacity-50"
                    >
                        Trước
                    </button>
                    <span className="px-3 py-2 bg-white rounded border">Trang {page} / {meta?.pages}</span>
                    <button
                        disabled={page === meta?.pages}
                        onClick={() => setPage(p => p + 1)}
                        className="btn btn-secondary text-sm disabled:opacity-50"
                    >
                        Sau
                    </button>
                </div>
            )}
        </div>
    );
}
