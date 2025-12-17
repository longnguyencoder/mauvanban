import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usersApi } from '../../../api/users';

export default function EditUser() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const [formData, setFormData] = useState({
        full_name: '',
        email: '',
        phone_number: '',
        role: 'user',
        is_active: true
    });

    const { data: userData, isLoading } = useQuery({
        queryKey: ['user', id],
        queryFn: () => usersApi.getById(id!), // Assume getById implemented
        enabled: !!id
    });

    useEffect(() => {
        if (userData?.data?.data) {
            const user = userData.data.data;
            setFormData({
                full_name: user.full_name || '',
                email: user.email || '',
                phone_number: user.phone_number || '', // Backend might return phone_number or phone. API says phone_number. User Interface says phone?
                role: user.role || 'user',
                is_active: user.is_active
            });
        }
    }, [userData]);

    const updateMutation = useMutation({
        mutationFn: (data: any) => usersApi.update(id!, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-users'] });
            queryClient.invalidateQueries({ queryKey: ['user', id] });
            alert('Cập nhật người dùng thành công!');
            navigate('/admin/users');
        },
        onError: (error: any) => {
            alert('Lỗi: ' + (error?.response?.data?.message || 'Có lỗi xảy ra'));
        }
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        // Handle checkbox manually if needed, but active is separate api? 
        // We can update role/info here.
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const onSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // Construct payload
        const payload = {
            full_name: formData.full_name,
            email: formData.email,
            phone_number: formData.phone_number,
            role: formData.role
        };
        updateMutation.mutate(payload);
    };

    if (isLoading) return <div>Đang tải...</div>;

    return (
        <div className="bg-white rounded-lg shadow-sm p-6 max-w-2xl mx-auto">
            <h2 className="text-2xl font-bold mb-6">Chỉnh sửa người dùng</h2>

            <form onSubmit={onSubmit} className="space-y-6">
                <div className="bg-yellow-50 p-4 rounded-md mb-6 text-sm text-yellow-800 border border-yellow-200">
                    Lưu ý: Chỉ được phép thay đổi Vai trò người dùng. Thông tin cá nhân do người dùng tự quản lý.
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Họ và tên</label>
                    <input
                        name="full_name"
                        value={formData.full_name}
                        readOnly
                        disabled
                        type="text"
                        className="w-full border-gray-300 rounded-md shadow-sm bg-gray-100 cursor-not-allowed p-2 border"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input
                        name="email"
                        value={formData.email}
                        readOnly
                        disabled
                        type="email"
                        className="w-full border-gray-300 rounded-md shadow-sm bg-gray-100 cursor-not-allowed p-2 border"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Số điện thoại</label>
                    <input
                        name="phone_number"
                        value={formData.phone_number}
                        readOnly
                        disabled
                        type="text"
                        className="w-full border-gray-300 rounded-md shadow-sm bg-gray-100 cursor-not-allowed p-2 border"
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
                        disabled={updateMutation.isPending}
                        className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                    >
                        {updateMutation.isPending ? 'Đang lưu...' : 'Lưu thay đổi'}
                    </button>
                </div>
            </form>
        </div>
    );
}
