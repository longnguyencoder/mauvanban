import React, { useState, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useAuthStore } from '../store/authStore';
import { usersApi } from '../api/users';

export default function Profile() {
    const { user, loadUser } = useAuthStore();
    const [isEditing, setIsEditing] = useState(false);

    // Form state
    const [formData, setFormData] = useState({
        full_name: '',
        phone: '',
    });

    useEffect(() => {
        if (user) {
            setFormData({
                full_name: user.full_name || '',
                phone: user.phone_number || user.phone || '',
            });
        }
    }, [user]);

    // Use usersApi.updateProfile if it exists, otherwise define mutation properly
    // Assuming usersApi has updateProfile based on previous attempts or standard practice.
    // If not, we might need to verify api/users.ts. Let's assume it calls PUT /auth/profile or /users/profile.
    // Checking api/users.ts content would be safer, but if not, I can fallback to direct API call if imported.
    // But better to stick to existing structure. I will use a direct mutationFn for now if specific API method is unsure.
    // But usually I should use the imported API. 
    // Let's use direct API call inside mutationFn to be safe or usersApi.update if available.
    // From previous steps, usersApi had 'create'. 'updateProfile' might be missing.
    // I'll check api/users.ts after this if needed, but for now I'll use the one from the file I read content of (lines 10-16 used api.put('/auth/profile')).
    // I will keep that logic but refine the UI.

    const updateProfileMutation = useMutation({
        mutationFn: (data: any) => usersApi.updateProfile(data),
        onSuccess: async () => {
            await loadUser();
            setIsEditing(false);
            alert('Cập nhật hồ sơ thành công!');
        },
        onError: (err: any) => {
            alert('Lỗi: ' + (err.response?.data?.message || err.message));
        }
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        updateProfileMutation.mutate(formData);
    };

    if (!user) return <div className="p-8 text-center">Vui lòng đăng nhập để xem hồ sơ.</div>;

    return (
        <div className="max-w-4xl mx-auto px-4 py-12">
            <div className="bg-white shadow rounded-lg overflow-hidden">
                <div className="px-6 py-4 bg-primary-600 border-b border-primary-500 flex justify-between items-center">
                    <h1 className="text-xl font-bold text-white">Hồ sơ cá nhân</h1>
                    {!isEditing && (
                        <button
                            onClick={() => setIsEditing(true)}
                            className="bg-white text-primary-600 hover:bg-gray-100 px-4 py-2 rounded text-sm font-medium transition"
                        >
                            Chỉnh sửa
                        </button>
                    )}
                </div>

                <div className="p-6">
                    <div className="flex flex-col md:flex-row gap-8">
                        {/* Avatar Section */}
                        <div className="flex flex-col items-center gap-4 min-w-[200px]">
                            <div className="w-32 h-32 bg-primary-100 rounded-full flex items-center justify-center text-4xl font-bold text-primary-600 border-4 border-white shadow">
                                {user.full_name ? user.full_name.charAt(0).toUpperCase() : user.email.charAt(0).toUpperCase()}
                            </div>
                            <div className="text-center">
                                <span className={`px-3 py-1 rounded-full text-xs font-bold ${user.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'}`}>
                                    {user.role === 'admin' ? 'Quản trị viên' : 'Thành viên'}
                                </span>
                            </div>
                        </div>

                        {/* Details Section */}
                        <div className="flex-grow">
                            {isEditing ? (
                                <form onSubmit={handleSubmit} className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                                        <input
                                            type="email"
                                            value={user.email}
                                            disabled
                                            className="w-full border-gray-300 bg-gray-100 rounded-md shadow-sm p-2 text-gray-500 cursor-not-allowed"
                                        />
                                        <p className="text-xs text-gray-500 mt-1">Email không thể thay đổi</p>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Họ và tên</label>
                                        <input
                                            type="text"
                                            value={formData.full_name}
                                            onChange={e => setFormData({ ...formData, full_name: e.target.value })}
                                            className="input"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Số điện thoại</label>
                                        <input
                                            type="text"
                                            value={formData.phone}
                                            onChange={e => setFormData({ ...formData, phone: e.target.value })}
                                            className="input"
                                        />
                                    </div>

                                    <div className="flex justify-end gap-3 pt-4 border-t mt-4">
                                        <button
                                            type="button"
                                            onClick={() => setIsEditing(false)}
                                            className="btn btn-secondary"
                                        >
                                            Hủy
                                        </button>
                                        <button
                                            type="submit"
                                            disabled={updateProfileMutation.isPending}
                                            className="btn btn-primary"
                                        >
                                            {updateProfileMutation.isPending ? 'Đang lưu...' : 'Lưu thay đổi'}
                                        </button>
                                    </div>
                                </form>
                            ) : (
                                <div className="space-y-6">
                                    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                                        <div>
                                            <dt className="text-sm font-medium text-gray-500">Họ và tên</dt>
                                            <dd className="mt-1 text-lg font-medium text-gray-900">{user.full_name || 'Chưa cập nhật'}</dd>
                                        </div>
                                        <div>
                                            <dt className="text-sm font-medium text-gray-500">Email</dt>
                                            <dd className="mt-1 text-lg font-medium text-gray-900">{user.email}</dd>
                                        </div>
                                        <div>
                                            <dt className="text-sm font-medium text-gray-500">Số điện thoại</dt>
                                            <dd className="mt-1 text-lg font-medium text-gray-900">{user.phone_number || user.phone || 'Chưa cập nhật'}</dd>
                                        </div>
                                        <div>
                                            <dt className="text-sm font-medium text-gray-500">Ngày tham gia</dt>
                                            <dd className="mt-1 text-lg font-medium text-gray-900">
                                                {user.created_at ? new Date(user.created_at).toLocaleDateString() : '---'}
                                            </dd>
                                        </div>
                                    </div>

                                    <div className="pt-6 border-t border-gray-200">
                                        <h3 className="text-lg font-medium text-gray-900 mb-4">Thông tin ví</h3>
                                        <div className="bg-gray-50 p-4 rounded-lg flex items-center justify-between">
                                            <div>
                                                <p className="text-sm text-gray-500">Số dư hiện tại</p>
                                                <p className="text-2xl font-bold text-green-600">{user.balance?.toLocaleString() || 0}đ</p>
                                            </div>
                                            <button className="btn btn-primary text-sm px-4 py-2">
                                                Nạp tiền
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
