import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { newsApi } from '../../api/news';
import { toast } from 'react-hot-toast';
import { SparklesIcon, DocumentPlusIcon, PhotoIcon, XMarkIcon } from '@heroicons/react/24/outline';

export default function AdminNews() {
    const queryClient = useQueryClient();
    const [topic, setTopic] = useState('');
    const [keywords, setKeywords] = useState('');
    const [thumbnailUrl, setThumbnailUrl] = useState('');
    const [preview, setPreview] = useState<{ title: string; summary: string; content: string } | null>(null);

    const generateMutation = useMutation({
        mutationFn: () => newsApi.generate(topic, keywords),
        onSuccess: (response) => {
            if (response.success) {
                setPreview(response.data);
                toast.success('Đã tạo xong bản nháp!');
            } else {
                toast.error(response.message || 'Lỗi khi tạo bài viết');
            }
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.message || 'Có lỗi xảy ra');
        }
    });

    const createMutation = useMutation({
        mutationFn: (data: any) => newsApi.create(data),
        onSuccess: (response) => {
            if (response.success) {
                toast.success('Bản tin đã được đăng thành công!');
                setPreview(null);
                setTopic('');
                setKeywords('');
                setThumbnailUrl('');
                queryClient.invalidateQueries({ queryKey: ['news'] });
            }
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.message || 'Lỗi khi lưu bài viết');
        }
    });

    const handleSave = () => {
        if (!preview) return;
        createMutation.mutate({
            ...preview,
            thumbnail_url: thumbnailUrl || 'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?q=80&w=2070&auto=format&fit=crop'
        });
    };

    return (
        <div className="max-w-6xl mx-auto space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Tạo tin tức bằng AI</h1>
                    <p className="text-gray-500">Nhập từ khóa và AI sẽ tự động viết bài giới thiệu dịch vụ chất lượng cao.</p>
                </div>
                <SparklesIcon className="w-10 h-10 text-primary-500 animate-pulse" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Input Sidebar */}
                <div className="lg:col-span-1 space-y-6">
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Chủ đề bài viết</label>
                            <textarea
                                value={topic}
                                onChange={(e) => setTopic(e.target.value)}
                                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all outline-none min-h-[100px]"
                                placeholder="Ví dụ: Dịch vụ tư vấn ly hôn gia đình nhanh chóng, trọn gói tại TP.HCM"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Từ khóa (cách nhau bằng dấu phẩy)</label>
                            <input
                                type="text"
                                value={keywords}
                                onChange={(e) => setKeywords(e.target.value)}
                                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all outline-none"
                                placeholder="ly hôn, luật sư, tư vấn, trọn gói..."
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Link ảnh đại diện (Unsplash/URL)</label>
                            <div className="flex space-x-2">
                                <input
                                    type="text"
                                    value={thumbnailUrl}
                                    onChange={(e) => setThumbnailUrl(e.target.value)}
                                    className="flex-grow px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-primary-500 outline-none transition-all"
                                    placeholder="https://..."
                                />
                                <button className="p-3 bg-gray-50 text-gray-400 rounded-xl hover:bg-gray-100">
                                    <PhotoIcon className="w-5 h-5" />
                                </button>
                            </div>
                        </div>

                        <button
                            onClick={() => generateMutation.mutate()}
                            disabled={generateMutation.isPending || !topic || !keywords}
                            className="w-full py-4 bg-primary-600 text-white rounded-xl font-bold flex items-center justify-center space-x-2 hover:bg-primary-700 disabled:bg-gray-300 transition-all shadow-lg shadow-primary-200"
                        >
                            {generateMutation.isPending ? (
                                <>
                                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                    <span>Đang suy nghĩ...</span>
                                </>
                            ) : (
                                <>
                                    <SparklesIcon className="w-5 h-5" />
                                    <span>Tạo bài viết AI</span>
                                </>
                            )}
                        </button>
                    </div>
                </div>

                {/* Preview Area */}
                <div className="lg:col-span-2">
                    {preview ? (
                        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                            <div className="px-6 py-4 bg-gray-50 border-b border-gray-100 flex items-center justify-between">
                                <span className="text-sm font-semibold text-gray-700">Xem trước bài viết</span>
                                <div className="flex space-x-2">
                                    <button
                                        onClick={() => setPreview(null)}
                                        className="p-1 hover:bg-gray-200 rounded-lg text-gray-500"
                                    >
                                        <XMarkIcon className="w-5 h-5" />
                                    </button>
                                </div>
                            </div>

                            <div className="p-8 space-y-6">
                                <h2 className="text-3xl font-bold text-gray-900 leading-tight">
                                    {preview.title}
                                </h2>

                                <div className="p-4 bg-primary-50 rounded-xl text-primary-800 text-sm leading-relaxed border border-primary-100">
                                    <strong>Tóm tắt:</strong> {preview.summary}
                                </div>

                                {thumbnailUrl && (
                                    <img src={thumbnailUrl} alt="Preview" className="w-full h-64 object-cover rounded-2xl shadow-inner" />
                                )}

                                <div
                                    className="prose prose-primary max-w-none text-gray-700"
                                    dangerouslySetInnerHTML={{ __html: preview.content }}
                                />

                                <div className="pt-8 flex justify-end space-x-4 border-t border-gray-100">
                                    <button
                                        onClick={() => setPreview(null)}
                                        className="px-6 py-3 text-gray-600 font-medium hover:bg-gray-50 rounded-xl transition-all"
                                    >
                                        Làm lại
                                    </button>
                                    <button
                                        onClick={handleSave}
                                        disabled={createMutation.isPending}
                                        className="px-8 py-3 bg-green-600 text-white font-bold rounded-xl hover:bg-green-700 transition-all shadow-lg shadow-green-100 flex items-center"
                                    >
                                        <DocumentPlusIcon className="w-5 h-5 mr-2" />
                                        {createMutation.isPending ? 'Đang lưu...' : 'Đăng bài viết ngay'}
                                    </button>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="h-full min-h-[500px] border-2 border-dashed border-gray-200 rounded-3xl flex flex-col items-center justify-center p-12 text-center text-gray-400 bg-gray-50/50">
                            <SparklesIcon className="w-16 h-16 mb-4 opacity-20" />
                            <h3 className="text-xl font-semibold mb-2">Chưa có bản nháp nào</h3>
                            <p className="max-w-sm">Nhập thông tin bên trái và nhấn nút Tạo để AI giúp bạn viết một bài tin tức chuyên nghiệp.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
