import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { documentsApi } from '../api/documents';
import { useAuthStore } from '../store/authStore';
import PaymentModal from '../components/common/PaymentModal';

export default function DocumentDetail() {
    const { slug } = useParams<{ slug: string }>();
    const { user } = useAuthStore();
    const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false);

    const { data, isLoading, error } = useQuery({
        queryKey: ['document', slug],
        queryFn: () => documentsApi.getBySlug(slug!),
        enabled: !!slug,
    });

    const doc = data?.data.data;

    const handleDownload = async () => {
        if (!doc) return;

        // If free, download immediately
        if (doc.price === 0) {
            try {
                const res = await documentsApi.download(doc.id);
                window.open(res.data.data.download_url, '_blank');
            } catch (err) {
                alert('Lỗi khi tải xuống. Vui lòng thử lại.');
            }
            return;
        }

        // If paid, show payment modal
        setIsPaymentModalOpen(true);
    };

    if (isLoading) return <div className="text-center py-20">Đang tải...</div>;
    if (error || !doc) return <div className="text-center py-20 text-red-500">Không tìm thấy văn bản</div>;

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <PaymentModal
                isOpen={isPaymentModalOpen}
                onClose={() => setIsPaymentModalOpen(false)}
                document={doc}
            />
            <div className="bg-white rounded-xl shadow-lg overflow-hidden">
                <div className="md:flex">
                    {/* Document Preview / Icon */}
                    <div className="md:w-1/3 bg-gray-100 p-8 flex items-center justify-center relative min-h-[300px]">
                        {doc.thumbnail_url ? (
                            <img
                                src={`http://localhost:5000${doc.thumbnail_url}`}
                                alt={doc.title}
                                className="w-full h-full object-contain rounded shadow-lg"
                            />
                        ) : (
                            <div className="text-center">
                                <span className="text-6xl block mb-4">
                                    {doc.file_type === 'pdf' ? '📄' : '📝'}
                                </span>
                                <div className="text-gray-500 font-medium uppercase tracking-wider">
                                    {doc.file_type}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Document Info */}
                    <div className="p-8 md:w-2/3">
                        <div className="flex items-center gap-2 text-sm text-primary-600 font-medium mb-2">
                            <span>{doc.category?.name || 'Chưa phân loại'}</span>
                            <span>•</span>
                            <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                        </div>

                        <h1 className="text-3xl font-bold text-gray-900 mb-4">
                            {doc.title}
                        </h1>

                        <div className="flex items-center gap-6 mb-8">
                            <div>
                                <span className="text-gray-500 text-sm">Lượt xem</span>
                                <p className="font-semibold text-lg">{doc.views_count}</p>
                            </div>
                            <div>
                                <span className="text-gray-500 text-sm">Lượt tải</span>
                                <p className="font-semibold text-lg">{doc.downloads_count}</p>
                            </div>
                            <div>
                                <span className="text-gray-500 text-sm">Giá</span>
                                <p className="font-bold text-2xl text-primary-600">
                                    {doc.price === 0 ? 'Miễn phí' : `${doc.price.toLocaleString()}đ`}
                                </p>
                            </div>
                        </div>

                        <p className="text-gray-600 mb-8 leading-relaxed">
                            {doc.description || 'Chưa có mô tả cho văn bản này.'}
                        </p>

                        <div className="flex gap-4">
                            <button
                                onClick={handleDownload}
                                className="btn btn-primary px-8 py-3 text-lg flex items-center gap-2 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all"
                            >
                                <span>{doc.price > 0 ? '💎' : '⬇️'}</span>
                                {doc.price > 0 ? 'Thanh toán & Tải xuống' : 'Tải xuống miễn phí'}
                            </button>

                            <button className="btn btn-secondary px-6 py-3">
                                ❤️ Lưu
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Content Preview if available */}
            {doc.content && (
                <div className="mt-12 bg-white rounded-xl shadow p-8">
                    <h2 className="text-xl font-bold mb-4">Nội dung xem trước</h2>
                    <div className="prose max-w-none text-gray-600">
                        {doc.content}
                    </div>
                </div>
            )}
        </div>
    );
}
