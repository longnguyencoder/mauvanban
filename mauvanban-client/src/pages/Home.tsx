import { Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { documentsApi } from '../api/documents';
import { categoriesApi } from '../api/categories';
import { API_BASE_URL } from '../api/axios';
import {
    BriefcaseIcon,
    AcademicCapIcon,
    ScaleIcon,
    BuildingOfficeIcon,
    HomeIcon,
    CurrencyDollarIcon,
    HeartIcon,
    DocumentTextIcon,
    ClipboardDocumentCheckIcon,
    FolderIcon,
    MagnifyingGlassIcon
} from '@heroicons/react/24/outline'; // Importing icons

export default function Home() {
    const navigate = useNavigate();

    // Fetch Featured Categories
    const { data: categories } = useQuery({
        queryKey: ['categories'],
        queryFn: categoriesApi.getAll,
    });

    // Fetch Latest Documents
    const { data: latestDocs } = useQuery({
        queryKey: ['documents', 'latest'],
        queryFn: () => documentsApi.getAll({ per_page: 8, sort: 'newest' }),
    });

    const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        const q = formData.get('q');
        if (q) {
            navigate(`/documents?q=${q}`);
        }
    };

    // Helper to get Icon (Same as Categories.tsx)
    const getIcon = (iconName: string) => {
        const className = "w-8 h-8 text-primary-600 group-hover:scale-110 transition-transform duration-300 object-contain";

        if (iconName && (iconName.startsWith('/') || iconName.startsWith('http'))) {
            const imageUrl = iconName.startsWith('/') ? `${API_BASE_URL}${iconName}` : iconName;
            return <img src={imageUrl} alt="icon" className={className} />;
        }

        switch (iconName) {
            case 'briefcase': return <BriefcaseIcon className={className} />;
            case 'graduation-cap': return <AcademicCapIcon className={className} />;
            case 'gavel': return <ScaleIcon className={className} />;
            case 'building': return <BuildingOfficeIcon className={className} />;
            case 'home': return <HomeIcon className={className} />;
            case 'dollar-sign': return <CurrencyDollarIcon className={className} />;
            case 'heartbeat': return <HeartIcon className={className} />;
            case 'file-text': return <DocumentTextIcon className={className} />;
            case 'file-contract': return <ClipboardDocumentCheckIcon className={className} />;
            default:
                if (iconName && !iconName.match(/^[a-z0-9-]+$/) && iconName.length < 5) {
                    return <div className="text-2xl group-hover:scale-110 transition-transform duration-300">{iconName}</div>;
                }
                return <FolderIcon className={className} />;
        }
    };

    return (
        <div>
            {/* Hero Section */}
            <div className="bg-gradient-to-r from-primary-600 to-secondary-600 text-white py-20 relative overflow-hidden">
                <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
                    <h1 className="text-4xl md:text-5xl font-bold mb-6 animate-fadeInDown">
                        Tìm kiếm biểu mẫu văn bản chuẩn
                    </h1>
                    <p className="text-xl text-blue-100 mb-10 max-w-2xl mx-auto animate-fadeInUp delay-100">
                        Hàng nghìn mẫu hợp đồng, đơn từ, văn bản hành chính, pháp luật được cập nhật liên tục và chính xác.
                    </p>

                    <form onSubmit={handleSearch} className="max-w-2xl mx-auto relative animate-fadeInUp delay-200">
                        <input
                            type="text"
                            name="q"
                            placeholder="Nhập tên văn bản, biểu mẫu bạn cần tìm..."
                            className="w-full pl-6 pr-32 py-4 rounded-full text-gray-900 shadow-2xl focus:outline-none focus:ring-4 focus:ring-primary-300 text-lg"
                        />
                        <button
                            type="submit"
                            className="absolute right-2 top-2 bg-secondary-500 hover:bg-secondary-600 text-white px-8 py-2.5 rounded-full font-bold transition-all shadow-md flex items-center gap-2"
                        >
                            <span>Tìm kiếm</span>
                        </button>
                    </form>

                    <div className="mt-8 flex justify-center gap-4 text-sm text-blue-100 animate-fadeInUp delay-300">
                        <span>Phổ biến:</span>
                        <Link to="/documents?q=hợp đồng" className="underline hover:text-white">Hợp đồng lao động</Link>
                        <Link to="/documents?q=đơn xin việc" className="underline hover:text-white">Đơn xin việc</Link>
                        <Link to="/documents?q=giấy ủy quyền" className="underline hover:text-white">Giấy ủy quyền</Link>
                    </div>
                </div>
            </div>

            {/* Featured Categories */}
            <div className="py-16 bg-gray-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <h2 className="text-3xl font-bold text-center text-gray-900 mb-12 uppercase tracking-wide">
                        Danh mục nổi bật
                    </h2>

                    <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
                        {(categories?.data?.data || []).slice(0, 10).map((cat: any) => (
                            <Link
                                key={cat.id}
                                to={`/documents?category=${cat.id}`}
                                className="bg-white p-6 rounded-xl shadow-sm hover:shadow-xl transition-all group flex flex-col items-center justify-center text-center border border-gray-100 hover:border-primary-200"
                            >
                                <div className="w-16 h-16 bg-primary-50 rounded-full flex items-center justify-center mb-4 group-hover:bg-primary-100 transition-colors">
                                    {getIcon(cat.icon)}
                                </div>
                                <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors truncate w-full">
                                    {cat.name}
                                </h3>
                            </Link>
                        ))}
                    </div>

                    <div className="text-center mt-12">
                        <Link
                            to="/categories"
                            className="text-primary-600 font-semibold hover:text-primary-700 flex items-center justify-center gap-2"
                        >
                            Xem tất cả danh mục <span>→</span>
                        </Link>
                    </div>
                </div>
            </div>

            {/* Latest Documents */}
            <div className="py-16">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-end mb-12">
                        <div>
                            <h2 className="text-3xl font-bold text-gray-900 mb-2">Văn bản mới nhất</h2>
                            <p className="text-gray-500">Cập nhật liên tục hàng ngày</p>
                        </div>
                        <Link to="/documents" className="btn btn-outline text-sm">
                            Xem tất cả
                        </Link>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                        {(latestDocs?.data?.data?.documents || []).map((doc: any) => (
                            <Link
                                key={doc.id}
                                to={`/documents/${doc.slug || doc.id}`}
                                className="card group hover:shadow-xl transition-all duration-300"
                            >
                                <div className="h-48 bg-gray-100 -mx-6 -mt-6 mb-4 flex items-center justify-center overflow-hidden relative">
                                    {doc.thumbnail_url ? (
                                        <img
                                            src={`${API_BASE_URL}${doc.thumbnail_url}`}
                                            alt={doc.title}
                                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                                        />
                                    ) : (
                                        <DocumentTextIcon className="w-16 h-16 text-gray-300 group-hover:text-gray-400 transition-colors" />
                                    )}
                                    <div className="absolute top-2 right-2 bg-white/90 backdrop-blur px-2 py-1 rounded text-xs font-bold uppercase shadow-sm">
                                        {doc.file_type}
                                    </div>
                                    {/* Overlay Action */}
                                    <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                        <span className="bg-white text-gray-900 px-4 py-2 rounded-full font-bold text-sm transform translate-y-4 group-hover:translate-y-0 transition-transform duration-300">
                                            Xem chi tiết
                                        </span>
                                    </div>
                                </div>
                                <h3 className="font-bold text-gray-900 mb-2 line-clamp-2 min-h-[3rem] group-hover:text-primary-600 transition-colors">
                                    {doc.title}
                                </h3>
                                <div className="flex justify-between items-center mt-4 pt-4 border-t border-gray-50">
                                    <span className="text-primary-600 font-bold">
                                        {doc.price === 0 ? 'Miễn phí' : `${doc.price.toLocaleString()}đ`}
                                    </span>
                                    <span className="text-xs text-gray-500 flex items-center gap-1">
                                        <span>👁️</span> {doc.views_count}
                                    </span>
                                </div>
                            </Link>
                        ))}
                    </div>
                </div>
            </div>

            {/* CTA Section */}
            <div className="bg-gray-900 text-white py-20">
                <div className="max-w-4xl mx-auto px-4 text-center">
                    <h2 className="text-3xl font-bold mb-6">Bạn cần hỗ trợ soạn thảo văn bản?</h2>
                    <p className="text-xl text-gray-300 mb-8">
                        Đội ngũ luật sư và chuyên gia của chúng tôi sẵn sàng hỗ trợ bạn soạn thảo, rà soát văn bản theo yêu cầu.
                    </p>
                    <div className="flex justify-center gap-4">
                        <a href="#" className="btn bg-primary-600 hover:bg-primary-700 text-white px-8 py-3 text-lg border-none shadow-lg shadow-primary-900/20">
                            Liên hệ tư vấn
                        </a>
                        <a href="tel:1900xxxx" className="btn bg-white/10 hover:bg-white/20 text-white px-8 py-3 text-lg border-white/20">
                            Gọi hotline: 1900 xxxx
                        </a>
                    </div>
                </div>
            </div>
        </div>
    );
}
