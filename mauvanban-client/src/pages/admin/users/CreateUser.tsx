import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { usersApi } from '../../../api/users';

export default function CreateUser() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const [formData, setFormData] = useState({
        full_name: '',
        email: '',
        password: '',
        phone_number: '', // Note: Backend uses phone_number alias in model/service logic I fixed
        role: 'user',
        is_active: true
    });

    const createMutation = useMutation({
        mutationFn: (data: any) => usersApi.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-users'] });
            alert('Thêm người dùng thành công!');
            navigate('/admin/users');
        },
        onError: (error: any) => {
            alert('Lỗi: ' + (error?.response?.data?.message || 'Có lỗi xảy ra'));
        }
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value, type } = e.target;
        const val = type === 'checkbox' ? (e.target as HTMLInputElement).checked : value;

        setFormData(prev => ({
            ...prev,
            [name]: val
        }));
    };

    const onSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        createMutation.mutate(formData);
    };

    return (
        <div className="bg-white rounded-lg shadow-sm p-6 max-w-2xl mx-auto">
            <h2 className="text-2xl font-bold mb-6">Thêm người dùng mới</h2>

            <form onSubmit={onSubmit} className="space-y-6">

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email (*)</label>
                    <input
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                        type="email"
                        className="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 p-2 border"
                        placeholder="example@email.com"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Mật khẩu (*)</label>
                    <input
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        required
                        type="password"
                        className="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 p-2 border"
                        placeholder="••••••"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Họ và tên</label>
                    <input
                        name="full_name"
                        value={formData.full_name}
                        onChange={handleChange}
                        type="text"
                        className="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 p-2 border"
                        placeholder="Nguyễn Văn A"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Số điện thoại</label>
                    <input
                        name="phone_number"
                        value={formData.phone_number}
                        onChange={handleChange}
                        type="text"
                        className="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 p-2 border"
                        placeholder="0912345678"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Vai trò</label>
                    <select
                        name="role"
                        value={formData.role}
                        onChange={handleChange}
                        className="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 p-2 border"
                    >
                        <option value="user">Người dùng (User)</option>
                        <option value="admin">Quản trị viên (Admin)</option>
                    </select>
                </div>

                <div className="flex items-center">
                    <input
                        name="is_active"
                        checked={formData.is_active}
                        onChange={handleChange}
                        type="checkbox"
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 block text-sm text-gray-900">
                        Kích hoạt ngay
                    </label>
                </div>

                <div className="flex justify-end gap-4 pt-4 border-t">
                    <button
                        type="button"
                        onClick={() => navigate('/admin/users')}
                        className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                    >
                        Hủy
                    </button>
                    <button
                        type="submit"
                        disabled={createMutation.isPending}
                        className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                    >
                        {createMutation.isPending ? 'Đang tạo...' : 'Tạo người dùng'}
                    </button>
                </div>
            </form>
        </div>
    );
}
