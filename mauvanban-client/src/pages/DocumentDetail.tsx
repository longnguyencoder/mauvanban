import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { documentsApi } from '../api/documents';
import { API_BASE_URL } from '../api/axios';
import { toast } from 'react-hot-toast';
import PaymentModal from '../components/common/PaymentModal';
import DocumentBadges from '../components/DocumentBadges';
import SEO from '../components/common/SEO';
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
    const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false);
    const [isSaved, setIsSaved] = useState(false);

    const { data, isLoading, error, refetch } = useQuery({
        queryKey: ['document', slug],
        queryFn: () => documentsApi.getBySlug(slug!),
        enabled: !!slug,
    });

    const doc = data?.data.data;

    const [downloadFiles, setDownloadFiles] = useState<any[]>([]);

    const handleDownload = async () => {
        if (!doc) return;

        // If free or already purchased, download
        if (doc.price === 0 || doc.has_purchased) {
            try {
                const res = await documentsApi.download(doc.id);
                const files = res.data.data.files || [];

                if (files.length === 1) {
                    window.open(files[0].download_url || res.data.data.download_url, '_blank');
                } else if (files.length > 1) {
                    setDownloadFiles(files);
                    toast.success('Văn bản gồm nhiều file. Vui lòng chọn file cần tải bên dưới.');
                    // Scroll to download section
                    document.getElementById('download-section')?.scrollIntoView({ behavior: 'smooth' });
                } else {
                    window.open(res.data.data.download_url, '_blank');
                }
            } catch (err) {
                toast.error('Lỗi khi tải xuống. Vui lòng thử lại.');
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
                // Automatically trigger download logic
                const res = await documentsApi.download(updatedDoc.id);
                const files = res.data.data.files || [];

                if (files.length === 1) {
                    window.open(files[0].download_url || res.data.data.download_url, '_blank');
                    toast.success('Thanh toán thành công! Đang tải tài liệu...');
                } else if (files.length > 1) {
                    setDownloadFiles(files);
                    toast.success('Thanh toán thành công! Vui lòng chọn file cần tải bên dưới.');
                    setTimeout(() => {
                        document.getElementById('download-section')?.scrollIntoView({ behavior: 'smooth' });
                    }, 500);
                } else {
                    window.open(res.data.data.download_url, '_blank');
                    toast.success('Thanh toán thành công! Đang tải tài liệu...');
                }
            } catch (err) {
                console.error('Download error after payment', err);
                alert('Thanh toán thành công! Bạn có thể nhấn nút Tải về để lấy tài liệu.');
            }
        }
    };

    const docSchema = doc ? {
        "@context": "https://schema.org",
        "@type": ["DigitalDocument", "Product"],
        "name": doc.title,
        "description": doc.description,
        "sku": doc.code,
        "offers": {
            "@type": "Offer",
            "price": doc.price,
            "priceCurrency": "VND",
            "availability": "https://schema.org/InStock"
        },
        "breadcrumb": {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Trang chủ",
                    "item": window.location.origin
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Văn bản",
                    "item": `${window.location.origin}/documents`
                },
                {
                    "@type": "ListItem",
                    "position": 3,
                    "name": doc.title,
                    "item": window.location.href
                }
            ]
        }
    } : null;

    return (
        <div className="min-h-screen gradient-bg py-8">
            {doc && (
                <SEO
                    title={doc.title}
                    description={doc.description || `Tải ${doc.title} chuẩn nhất. File ${doc.file_type} chất lượng, đầy đủ nội dung.`}
                    schema={docSchema}
                />
            )}
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
                        <li><Link to="/" className="hover:text-primary-600">Trang chủ</Link></li>
                        <li>/</li>
                        <li><Link to="/documents" className="hover:text-primary-600">Văn bản</Link></li>
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

                                {/* Multi-file download section */}
                                {(doc.has_purchased || doc.price === 0) && downloadFiles.length > 0 && (
                                    <div id="download-section" className="mt-8 p-6 bg-green-50 rounded-2xl border-2 border-green-200 animate-fade-in">
                                        <h3 className="text-lg font-bold text-green-800 mb-4 flex items-center gap-2">
                                            <ArrowDownTrayIcon className="w-5 h-5" />
                                            Danh sách file tải về:
                                        </h3>
                                        <div className="grid grid-cols-1 gap-3">
                                            {downloadFiles.map((file, idx) => (
                                                <div key={file.id || idx} className="flex items-center justify-between p-4 bg-white rounded-xl shadow-sm border border-green-100 hover:border-green-300 transition-colors">
                                                    <div className="flex items-center gap-3">
                                                        <div className="bg-green-100 p-2 rounded-lg">
                                                            <DocumentIcon className="w-5 h-5 text-green-600" />
                                                        </div>
                                                        <div>
                                                            <p className="font-bold text-gray-900 text-sm line-clamp-1">{file.original_filename}</p>
                                                            <p className="text-xs text-gray-500 uppercase">{file.file_type}</p>
                                                        </div>
                                                    </div>
                                                    <a
                                                        href={file.download_url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="btn bg-green-600 hover:bg-green-700 text-white py-2 px-4 shadow-md text-sm font-bold"
                                                    >
                                                        TẢI FILE {idx + 1}
                                                    </a>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

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

                    {/* Right Column - Related Documents Sidebar */}
                    <div className="lg:col-span-1">
                        {doc.related_documents && doc.related_documents.length > 0 ? (
                            <div className="bg-white rounded-2xl shadow-xl overflow-hidden p-6 sticky top-8">
                                <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2 pb-4 border-b">
                                    <DocumentIcon className="w-5 h-5 text-primary-600" />
                                    Văn bản liên quan
                                    <span className="text-[10px] bg-red-500 text-white px-1.5 py-0.5 rounded-full animate-pulse">MỚI</span>
                                </h2>
                                <div className="space-y-6">
                                    {doc.related_documents.map((relatedDoc: any) => (
                                        <Link
                                            key={relatedDoc.id}
                                            to={`/documents/${relatedDoc.slug || relatedDoc.id}`}
                                            className="group flex gap-3"
                                        >
                                            <div className="w-16 h-20 bg-gray-50 rounded flex-shrink-0 flex items-center justify-center overflow-hidden border border-gray-100">
                                                {relatedDoc.thumbnail_url ? (
                                                    <img
                                                        src={`${API_BASE_URL}${relatedDoc.thumbnail_url}`}
                                                        alt={relatedDoc.title}
                                                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                                                    />
                                                ) : (
                                                    <DocumentIcon className="w-8 h-8 text-gray-200" />
                                                )}
                                            </div>
                                            <div className="flex-1 flex flex-col justify-between py-0.5">
                                                <div>
                                                    <h3 className="font-bold text-gray-900 line-clamp-2 text-xs leading-normal group-hover:text-primary-600 transition-colors">
                                                        {relatedDoc.title}
                                                    </h3>
                                                    <p className="text-[10px] text-gray-400 mt-1 uppercase tracking-tight">
                                                        Mã: {relatedDoc.code || 'BA-' + relatedDoc.id.substring(0, 4).toUpperCase()}
                                                    </p>
                                                </div>
                                                <div className="flex justify-between items-center text-[11px] mt-1">
                                                    <span className="text-primary-600 font-bold">
                                                        {relatedDoc.price === 0 ? 'Miễn phí' : `${relatedDoc.price.toLocaleString()}đ`}
                                                    </span>
                                                    <span className="text-gray-400 flex items-center gap-0.5">
                                                        <EyeIcon className="w-2.5 h-2.5" /> {relatedDoc.views_count}
                                                    </span>
                                                </div>
                                            </div>
                                        </Link>
                                    ))}
                                </div>
                                <div className="mt-8">
                                    <Link
                                        to={`/documents?category=${doc.category_id}`}
                                        className="w-full btn btn-secondary text-sm"
                                    >
                                        Xem thêm cùng danh mục
                                    </Link>
                                </div>
                            </div>
                        ) : (
                            <div className="bg-primary-900 text-white rounded-2xl shadow-xl p-8 sticky top-8">
                                <h3 className="text-xl font-bold mb-4">Bạn cần hỗ trợ?</h3>
                                <p className="text-blue-100 text-sm mb-6 leading-relaxed">
                                    Đội ngũ chuyên gia của chúng tôi sẵn sàng hỗ trợ bạn soạn thảo văn bản chuẩn pháp lý.
                                </p>
                                <a href="/contact" className="w-full btn bg-white text-primary-900 hover:bg-blue-50 border-none font-bold">
                                    Liên hệ ngay
                                </a>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
