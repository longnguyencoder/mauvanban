import { useState } from 'react';
import { API_BASE_URL } from '../api/axios';

export default function Contact() {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        subject: '',
        message: ''
    });

    const [sending, setSending] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSending(true);
        try {
            await fetch(`${API_BASE_URL}/api/contact`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });
            alert('Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi sớm nhất.');
            setFormData({ name: '', email: '', subject: '', message: '' });
        } catch (error) {
            alert('Có lỗi xảy ra khi gửi tin nhắn. Vui lòng thử lại sau.');
            console.error(error);
        } finally {
            setSending(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    return (
        <div className="bg-gray-50 min-h-screen py-12">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center mb-12">
                    <h1 className="text-3xl font-bold text-gray-900 mb-4">Liên hệ với chúng tôi</h1>
                    <p className="text-gray-500 max-w-2xl mx-auto">
                        Chúng tôi luôn lắng nghe ý kiến đóng góp của bạn để cải thiện chất lượng dịch vụ.
                        Vui lòng để lại thông tin liên hệ bên dưới.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                    {/* Contact Info */}
                    <div className="bg-white rounded-lg shadow-lg p-8">
                        <h2 className="text-xl font-bold text-gray-900 mb-6">Thông tin liên hệ</h2>

                        <div className="space-y-6">
                            <div className="flex items-start gap-4">
                                <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 flex-shrink-0">
                                    📍
                                </div>
                                <div>
                                    <h3 className="font-medium text-gray-900">Địa chỉ</h3>
                                    <p className="text-gray-600 mt-1">
                                        281/2/1 Bình Lợi, phường Bình Lợi Trung, <br />
                                        Thành phố Hồ Chí Minh
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-start gap-4">
                                <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 flex-shrink-0">
                                    📞
                                </div>
                                <div>
                                    <h3 className="font-medium text-gray-900">Hotline</h3>
                                    <p className="text-gray-600 mt-1 font-bold text-lg">0398.481.719</p>
                                    <p className="text-xs text-gray-500">Hỗ trợ 24/7</p>
                                </div>
                            </div>

                            <div className="flex items-start gap-4">
                                <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 flex-shrink-0">
                                    ✉️
                                </div>
                                <div>
                                    <h3 className="font-medium text-gray-900">Email</h3>
                                    <p className="text-gray-600 mt-1">hotro@mauvanban.vn</p>
                                </div>
                            </div>
                        </div>

                        {/* Map (Optional - Placeholder) */}
                        <div className="mt-8 bg-gray-200 h-48 rounded-lg flex items-center justify-center text-gray-500">
                            (Bản đồ Google Maps)
                        </div>
                    </div>

                    {/* Contact Form */}
                    <div className="bg-white rounded-lg shadow-lg p-8">
                        <h2 className="text-xl font-bold text-gray-900 mb-6">Gửi tin nhắn</h2>
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div>
                                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">Họ và tên</label>
                                <input
                                    type="text"
                                    id="name"
                                    name="name"
                                    required
                                    value={formData.name}
                                    onChange={handleChange}
                                    className="input w-full"
                                    placeholder="Nhập họ tên của bạn"
                                />
                            </div>

                            <div>
                                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                                <input
                                    type="email"
                                    id="email"
                                    name="email"
                                    required
                                    value={formData.email}
                                    onChange={handleChange}
                                    className="input w-full"
                                    placeholder="example@email.com"
                                />
                            </div>

                            <div>
                                <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-1">Tiêu đề</label>
                                <input
                                    type="text"
                                    id="subject"
                                    name="subject"
                                    required
                                    value={formData.subject}
                                    onChange={handleChange}
                                    className="input w-full"
                                    placeholder="Bạn cần hỗ trợ gì?"
                                />
                            </div>

                            <div>
                                <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-1">Nội dung</label>
                                <textarea
                                    id="message"
                                    name="message"
                                    required
                                    rows={4}
                                    value={formData.message}
                                    onChange={handleChange}
                                    className="input w-full"
                                    placeholder="Chi tiết yêu cầu của bạn..."
                                />
                            </div>

                            <button type="submit" disabled={sending} className="btn btn-primary w-full py-3">
                                {sending ? 'Đang gửi...' : 'Gửi tin nhắn'}
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
}
