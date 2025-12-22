import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { documentsApi } from '../api/documents';
import { API_BASE_URL } from '../api/axios';
import { useAuthStore } from '../store/authStore';
import { toast } from 'react-hot-toast';
import PaymentModal from '../components/common/PaymentModal';
import DocumentBadges from '../components/DocumentBadges';
import DocumentGuideSection from '../components/DocumentGuideSection';
import {
    ArrowDownTrayIcon,
    BookmarkIcon,
    ShareIcon,
    FlagIcon,
    EyeIcon,
    ArrowDownCircleIcon,
    DocumentIcon
} from '@heroicons/react/24/outline';
import { BookmarkIcon as BookmarkSolidIcon } from '@heroicons/react/24/solid';

export default function DocumentDetail() {
    const { slug } = useParams<{ slug: string }>();
    const { user } = useAuthStore();
    const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false);
    const [isSaved, setIsSaved] = useState(false);

    const { data, isLoading, error, refetch } = useQuery({
        queryKey: ['document', slug],
        queryFn: () => documentsApi.getBySlug(slug!),
        enabled: !!slug,
    });

    const doc = data?.data.data;

    const handleDownload = async () => {
        if (!doc) return;

        // If free or already purchased, download immediately
        if (doc.price === 0 || doc.has_purchased) {
            try {
                const res = await documentsApi.download(doc.id);
                window.open(res.data.data.download_url, '_blank');
            } catch (err) {
                alert('Lỗi khi tải xuống. Vui lòng thử lại.');
            }
            return;
        }

        // If paid and not purchased, show payment modal
        setIsPaymentModalOpen(true);
    };

    const handleSave = () => {
        setIsSaved(!isSaved);
        // TODO: Implement save to favorites functionality
    };

    const handleShare = () => {
        // Copy URL to clipboard
        navigator.clipboard.writeText(window.location.href);
        alert('Đã sao chép liên kết!');
    };

    const handleReport = () => {
        alert('Chức năng báo cáo đang được phát triển.');
    };

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Đang tải...</p>
                </div>
            </div>
        );
    }

    if (error || !doc) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <p className="text-red-500 text-xl mb-4">Không tìm thấy văn bản</p>
                    <a href="/documents" className="btn btn-primary">
                        Quay lại danh sách
                    </a>
                </div>
            </div>
        );
    }

    const handlePaymentSuccess = async () => {
        setIsPaymentModalOpen(false);
        // Refetch document data to update has_purchased status
        const { data: updatedData } = await refetch();

        const updatedDoc = updatedData?.data.data;
        if (updatedDoc && updatedDoc.has_purchased) {
            try {
                // Automatically trigger download
                const res = await documentsApi.download(updatedDoc.id);
                window.open(res.data.data.download_url, '_blank');
                toast.success('Thanh toán thành công! Đang tải tài liệu...');
            } catch (err) {
                console.error('Download error after payment', err);
                alert('Thanh toán thành công! Bạn có thể nhấn nút Tải về để lấy tài liệu.');
            }
        }
    };

    return (
        <div className="min-h-screen gradient-bg py-8">
            <PaymentModal
                isOpen={isPaymentModalOpen}
                onClose={() => setIsPaymentModalOpen(false)}
                document={doc}
                onSuccess={handlePaymentSuccess}
            />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Breadcrumb */}
                <nav className="mb-6 text-sm">
                    <ol className="flex items-center space-x-2 text-gray-600">
                        <li><a href="/" className="hover:text-primary-600">Trang chủ</a></li>
                        <li>/</li>
                        <li><a href="/documents" className="hover:text-primary-600">Văn bản</a></li>
                        <li>/</li>
                        <li className="text-gray-900 font-medium truncate max-w-xs">{doc.title}</li>
                    </ol>
                </nav>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Left Column - Document Details */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Header Card */}
                        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
                            <div className="p-8">
                                {/* Document Code */}
                                <div className="mb-4">
                                    <span className="inline-block bg-primary-100 text-primary-700 px-4 py-2 rounded-lg font-bold text-sm">
                                        {doc.code || 'MV-' + doc.id.substring(0, 6).toUpperCase()}
                                    </span>
                                </div>

                                {/* Title */}
                                <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4 leading-tight">
                                    {doc.title}
                                </h1>

                                {/* Badges */}
                                <DocumentBadges />

                                {/* Meta Info */}
                                <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-gray-600 mb-6 pb-6 border-b border-gray-200">
                                    <span className="flex items-center gap-1 bg-gray-50 px-2 py-1 rounded">
                                        <EyeIcon className="w-4 h-4 text-gray-400" />
                                        <span className="font-medium text-gray-900">{doc.views_count || 0}</span>
                                        <span className="text-gray-500">lượt xem</span>
                                    </span>
                                    <span className="flex items-center gap-1 bg-gray-50 px-2 py-1 rounded">
                                        <ArrowDownCircleIcon className="w-4 h-4 text-gray-400" />
                                        <span className="font-medium text-gray-900">{doc.downloads_count || 0}</span>
                                        <span className="text-gray-500">lượt tải</span>
                                    </span>
                                    {doc.category && (
                                        <span className="bg-primary-50 text-primary-700 px-2 py-1 rounded font-medium">
                                            {doc.category.name}
                                        </span>
                                    )}
                                </div>

                                {/* Description */}
                                <div className="mb-8">
                                    <p className="text-gray-700 leading-relaxed text-lg">
                                        {doc.description || 'Đơn xin việc là văn bản trình bày nguyện vọng, kỹ năng và kinh nghiệm của ứng viên để thuyết phục nhà tuyển dụng trao cơ hội làm việc.'}
                                    </p>
                                </div>

                                {/* Action Buttons */}
                                <div className="flex flex-col sm:flex-row gap-4">
                                    <button
                                        onClick={handleDownload}
                                        className={`btn-download flex-1 sm:flex-none justify-center ${doc.has_purchased ? 'bg-green-600 hover:bg-green-700' : ''}`}
                                    >
                                        <ArrowDownTrayIcon className="w-6 h-6 flex-shrink-0" />
                                        <div className="flex flex-col sm:flex-row items-center gap-1 sm:gap-3">
                                            <span className="whitespace-nowrap">{doc.has_purchased ? 'TẢI VỀ (ĐÃ MUA)' : 'TẢI NGAY'}</span>
                                            {!doc.has_purchased && (
                                                <span className="font-bold opacity-90 text-sm sm:text-lg">
                                                    {doc.price === 0 ? 'MIỄN PHÍ' : `${doc.price.toLocaleString()}₫`}
                                                </span>
                                            )}
                                        </div>
                                    </button>
                                </div>

                                {/* Secondary Actions */}
                                <div className="flex flex-wrap gap-3 mt-4">
                                    <button
                                        onClick={handleSave}
                                        className="btn btn-secondary flex items-center gap-2"
                                    >
                                        {isSaved ? (
                                            <BookmarkSolidIcon className="w-5 h-5 text-primary-600" />
                                        ) : (
                                            <BookmarkIcon className="w-5 h-5" />
                                        )}
                                        Lưu
                                    </button>
                                    <button
                                        onClick={handleShare}
                                        className="btn btn-secondary flex items-center gap-2"
                                    >
                                        <ShareIcon className="w-5 h-5" />
                                        Chia sẻ
                                    </button>
                                    <button
                                        onClick={handleReport}
                                        className="btn btn-secondary flex items-center gap-2"
                                    >
                                        <FlagIcon className="w-5 h-5" />
                                        Báo cáo
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Document Preview Card */}
                        <div className="bg-white rounded-2xl shadow-xl overflow-hidden p-8">
                            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                                <DocumentIcon className="w-6 h-6 text-primary-600" />
                                Xem trước văn bản
                            </h2>

                            <div className="document-preview space-y-8">
                                {/* Case 1: Multiple Files */}
                                {doc.files && doc.files.length > 0 ? (
                                    doc.files.map((file: any, index: number) => (
                                        <div key={file.id || index} className="mb-8 last:mb-0">
                                            <h3 className="font-semibold text-gray-700 mb-2 flex items-center gap-2">
                                                <span className="bg-gray-200 text-gray-700 w-6 h-6 rounded-full flex items-center justify-center text-xs">
                                                    {index + 1}
                                                </span>
                                                {file.original_filename || `Tài liệu ${index + 1}`}
                                            </h3>

                                            {file.preview_url ? (
                                                <div className="relative group">
                                                    <img
                                                        src={`${API_BASE_URL}${file.preview_url}`}
                                                        alt={`Preview ${file.original_filename}`}
                                                        className="w-full h-auto rounded-lg shadow-sm border border-gray-100"
                                                    />
                                                    <div className="document-watermark">
                                                        Xem trước trang 1
                                                    </div>
                                                </div>
                                            ) : (
                                                /* Fallback: If it's the first file and we have a document thumbnail (manual upload), show it */
                                                (index === 0 && doc.thumbnail_url) ? (
                                                    <div className="relative group">
                                                        <img
                                                            src={`${API_BASE_URL}${doc.thumbnail_url}`}
                                                            alt={`Preview ${file.original_filename}`}
                                                            className="w-full h-auto rounded-lg shadow-sm border border-gray-100"
                                                        />
                                                        <div className="document-watermark">
                                                            Ảnh bìa văn bản
                                                        </div>
                                                    </div>
                                                ) : (
                                                    <div className="bg-gray-50 rounded-lg p-8 text-center border border-gray-200">
                                                        <div className="text-4xl mb-2">
                                                            {file.file_type === 'pdf' ? '📄' : '📝'}
                                                        </div>
                                                        <p className="text-sm text-gray-500">{file.original_filename}</p>
                                                        <p className="text-xs text-gray-400 mt-1">Không có bản xem trước</p>
                                                    </div>
                                                )
                                            )}
                                        </div>
                                    ))
                                ) : (
                                    /* Case 2: Legacy Single File/Thumbnail */
                                    doc.thumbnail_url ? (
                                        <div className="relative">
                                            <img
                                                src={`${API_BASE_URL}${doc.thumbnail_url}`}
                                                alt={doc.title}
                                                className="w-full h-auto rounded-lg"
                                            />
                                            <div className="document-watermark">
                                                1/2 trang
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg p-16 text-center">
                                            <div className="text-8xl mb-4">
                                                {doc.file_type === 'pdf' ? '📄' : '📝'}
                                            </div>
                                            <p className="text-gray-500 font-medium uppercase tracking-wider">
                                                {doc.file_type}
                                            </p>
                                            <p className="text-gray-400 text-sm mt-2">
                                                Xem trước không khả dụng
                                            </p>
                                        </div>
                                    )
                                )}
                            </div>

                            {/* Content Preview */}
                            {doc.content && (
                                <div className="mt-8 pt-8 border-t border-gray-200">
                                    <h3 className="text-lg font-bold text-gray-900 mb-4">Nội dung mẫu</h3>
                                    <div className="prose max-w-none text-gray-600 bg-gray-50 rounded-lg p-6">
                                        {doc.content}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Right Column - Guide Navigation */}
                    <div className="lg:col-span-1">
                        <DocumentGuideSection />
                    </div>
                </div>
            </div>
        </div>
    );
}
