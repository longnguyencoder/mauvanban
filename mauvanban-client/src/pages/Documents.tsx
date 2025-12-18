import { Link, useSearchParams } from 'react-router-dom';
import { documentsApi, Document } from '../api/documents';
import { API_BASE_URL } from '../api/axios';
import { categoriesApi, Category } from '../api/categories';
import { useQuery } from '@tanstack/react-query';

export default function Documents() {
    const [searchParams, setSearchParams] = useSearchParams();
    const page = Number(searchParams.get('page')) || 1;
    const search = searchParams.get('q') || '';
    const categoryId = searchParams.get('category') || undefined;

    // Fetch Categories
    const { data: categoriesData } = useQuery({
        queryKey: ['categories'],
        queryFn: categoriesApi.getAll,
    });

    // Fetch Documents
    const { data: documentsData, isLoading } = useQuery({
        queryKey: ['documents', page, search, categoryId],
        queryFn: () => documentsApi.getAll({
            page,
            q: search,
            category_id: categoryId,
            per_page: 12
        }),
    });

    const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        const q = formData.get('q') as string;
        setSearchParams({ q, page: '1' });
    };

    const handleCategoryChange = (id: number | string | undefined) => {
        if (id) {
            setSearchParams({ category: id.toString(), page: '1' });
        } else {
            setSearchParams({ page: '1' });
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex flex-col md:flex-row gap-8">

                {/* Sidebar Filter */}
                <div className="w-full md:w-64 flex-shrink-0">
                    <div className="bg-white rounded-xl shadow-md overflow-hidden sticky top-8">
                        <div className="bg-gradient-to-r from-primary-600 to-primary-700 px-6 py-4">
                            <h3 className="font-bold text-lg text-white flex items-center gap-2">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                                </svg>
                                Danh mục
                            </h3>
                        </div>
                        <ul className="py-2">
                            <li>
                                <button
                                    onClick={() => handleCategoryChange(undefined)}
                                    className={`block w-full text-left px-6 py-3 transition-all duration-200 ${!categoryId
                                        ? 'bg-primary-50 text-primary-700 font-semibold border-l-4 border-primary-600'
                                        : 'text-gray-700 hover:bg-gray-50 border-l-4 border-transparent hover:border-gray-300'
                                        }`}
                                >
                                    <span className="flex items-center gap-2">
                                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                            <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
                                        </svg>
                                        Tất cả
                                    </span>
                                </button>
                            </li>
                            {(categoriesData?.data?.data || []).map((cat: Category) => (
                                <li key={cat.id}>
                                    <button
                                        onClick={() => handleCategoryChange(cat.id)}
                                        className={`block w-full text-left px-6 py-3 transition-all duration-200 ${categoryId === cat.id
                                            ? 'bg-primary-50 text-primary-700 font-semibold border-l-4 border-primary-600'
                                            : 'text-gray-700 hover:bg-gray-50 border-l-4 border-transparent hover:border-gray-300'
                                            }`}
                                    >
                                        <span className="flex items-center gap-2">
                                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                                <path fillRule="evenodd" d="M2 6a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1H8a3 3 0 00-3 3v1.5a1.5 1.5 0 01-3 0V6z" clipRule="evenodd" />
                                                <path d="M6 12a2 2 0 012-2h8a2 2 0 012 2v2a2 2 0 01-2 2H2h2a2 2 0 002-2v-2z" />
                                            </svg>
                                            {cat.name}
                                        </span>
                                    </button>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

                {/* Main Content */}
                <div className="flex-1">
                    {/* Search Bar */}
                    <div className="mb-8">
                        <form onSubmit={handleSearch} className="relative">
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                    <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                    </svg>
                                </div>
                                <input
                                    type="text"
                                    name="q"
                                    defaultValue={search}
                                    onChange={(e) => {
                                        if (e.target.value === '') {
                                            const newParams = Object.fromEntries(searchParams);
                                            setSearchParams({ ...newParams, q: '', page: '1' });
                                        }
                                    }}
                                    placeholder="Tìm kiếm văn bản, biểu mẫu, hợp đồng..."
                                    className="block w-full pl-12 pr-32 py-4 text-base border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200"
                                />
                                <div className="absolute inset-y-0 right-0 flex items-center pr-2">
                                    <button
                                        type="submit"
                                        className="bg-primary-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all duration-200 shadow-sm hover:shadow-md"
                                    >
                                        Tìm kiếm
                                    </button>
                                </div>
                            </div>
                        </form>
                    </div>

                    {/* Document Grid */}
                    {isLoading ? (
                        <div className="text-center py-12">Đang tải...</div>
                    ) : (
                        <>
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                                {(documentsData?.data?.data?.documents || []).map((doc: Document) => (
                                    <Link
                                        key={doc.id}
                                        to={`/documents/${doc.slug || doc.id}`} // Use slug if available, else ID
                                        className="card hover:shadow-lg transition-shadow duration-200 flex flex-col group h-full"
                                    >
                                        <div className="h-48 bg-gray-100 -mx-6 -mt-6 mb-4 flex items-center justify-center overflow-hidden relative">
                                            {doc.thumbnail_url ? (
                                                <img
                                                    src={`${API_BASE_URL}${doc.thumbnail_url}`}
                                                    alt={doc.title}
                                                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                                                />
                                            ) : (
                                                <div className="text-4xl text-gray-400">
                                                    {doc.file_type === 'pdf' ? '📄' : '📝'}
                                                </div>
                                            )}
                                            {/* Overlay for type if thumbnail exists */}
                                            {doc.thumbnail_url && (
                                                <div className="absolute top-2 right-2 bg-white/90 backdrop-blur px-2 py-1 rounded text-xs font-bold uppercase shadow-sm">
                                                    {doc.file_type}
                                                </div>
                                            )}
                                        </div>
                                        <div className="flex-1">
                                            <h3 className="font-bold text-lg mb-2 line-clamp-2" title={doc.title}>
                                                {doc.title}
                                            </h3>
                                            <p className="text-gray-500 text-sm mb-2">
                                                {doc.category?.name}
                                            </p>
                                            <div className="flex justify-between items-center mt-auto">
                                                <span className="text-primary-600 font-bold">
                                                    {doc.price === 0 ? 'Miễn phí' : `${doc.price.toLocaleString()}đ`}
                                                </span>
                                                <span className="text-gray-400 text-xs">
                                                    {doc.views_count} lượt xem
                                                </span>
                                            </div>
                                        </div>
                                    </Link>
                                ))}
                            </div>

                            {/* No Results */}
                            {(documentsData?.data?.data?.documents || []).length === 0 && (
                                <div className="text-center py-12 text-gray-500">
                                    Không tìm thấy văn bản nào.
                                </div>
                            )}

                            {/* Pagination */}
                            {documentsData?.data?.data && documentsData.data.data.pages > 1 && (
                                <div className="mt-8 flex justify-center gap-2">
                                    <button
                                        disabled={page === 1}
                                        onClick={() => setSearchParams({ ...Object.fromEntries(searchParams), page: (page - 1).toString() })}
                                        className="btn btn-secondary disabled:opacity-50"
                                    >
                                        Trước
                                    </button>
                                    <span className="px-4 py-2 text-gray-600">
                                        Trang {page} / {documentsData.data.data.pages}
                                    </span>
                                    <button
                                        disabled={page === documentsData.data.data.pages}
                                        onClick={() => setSearchParams({ ...Object.fromEntries(searchParams), page: (page + 1).toString() })}
                                        className="btn btn-secondary disabled:opacity-50"
                                    >
                                        Sau
                                    </button>
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
