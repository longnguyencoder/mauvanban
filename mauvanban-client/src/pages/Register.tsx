import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export default function Register() {
    const navigate = useNavigate();
    const register = useAuthStore((state) => state.register);
    const isLoading = useAuthStore((state) => state.isLoading);
    const error = useAuthStore((state) => state.error);
    const clearError = useAuthStore((state) => state.clearError);

    const [formData, setFormData] = useState({
        email: '',
        password: '',
        confirmPassword: '',
        full_name: '',
        phone: '',
    });

    const [validationError, setValidationError] = useState('');

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
        if (validationError) setValidationError('');
        if (error) clearError();
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (formData.password !== formData.confirmPassword) {
            setValidationError('Mật khẩu nhập lại không khớp');
            return;
        }

        try {
            await register({
                email: formData.email,
                password: formData.password,
                full_name: formData.full_name,
                phone: formData.phone,
            });
            navigate('/');
        } catch (err) {
            // API error handled by store
        }
    };

    return (
        <div className="min-h-[80vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8">
                <div>
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                        Đăng ký tài khoản
                    </h2>
                    <p className="mt-2 text-center text-sm text-gray-600">
                        Đã có tài khoản?{' '}
                        <Link to="/login" className="font-medium text-primary-600 hover:text-primary-500">
                            Đăng nhập ngay
                        </Link>
                    </p>
                </div>

                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    {(error || validationError) && (
                        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded text-sm">
                            {error || validationError}
                        </div>
                    )}

                    <div className="rounded-md shadow-sm space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Email</label>
                            <input
                                name="email"
                                type="email"
                                required
                                className="input mt-1"
                                value={formData.email}
                                onChange={handleChange}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">Họ và tên</label>
                            <input
                                name="full_name"
                                type="text"
                                required
                                className="input mt-1"
                                value={formData.full_name}
                                onChange={handleChange}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">Số điện thoại</label>
                            <input
                                name="phone"
                                type="tel"
                                className="input mt-1"
                                value={formData.phone}
                                onChange={handleChange}
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Mật khẩu</label>
                                <input
                                    name="password"
                                    type="password"
                                    required
                                    className="input mt-1"
                                    value={formData.password}
                                    onChange={handleChange}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Nhập lại</label>
                                <input
                                    name="confirmPassword"
                                    type="password"
                                    required
                                    className="input mt-1"
                                    value={formData.confirmPassword}
                                    onChange={handleChange}
                                />
                            </div>
                        </div>
                    </div>

                    <div>
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full btn btn-primary py-3"
                        >
                            {isLoading ? 'Đang xử lý...' : 'Đăng ký'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
