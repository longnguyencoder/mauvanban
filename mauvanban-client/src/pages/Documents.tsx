import { Link, useSearchParams } from 'react-router-dom';
import { documentsApi, Document } from '../api/documents';
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
                    <div className="bg-white p-4 rounded-lg shadow-sm">
                        <h3 className="font-bold text-lg mb-4">Danh mục</h3>
                        <ul className="space-y-2">
                            <li>
                                <button
                                    onClick={() => handleCategoryChange(undefined)}
                                    className={`block w-full text-left px-2 py-1 rounded ${!categoryId ? 'bg-primary-50 text-primary-600 font-medium' : 'text-gray-600 hover:bg-gray-50'}`}
                                >
                                    Tất cả
                                </button>
                            </li>
                            {(categoriesData?.data?.data || []).map((cat: Category) => (
                                <li key={cat.id}>
                                    <button
                                        onClick={() => handleCategoryChange(cat.id)}
                                        className={`block w-full text-left px-2 py-1 rounded ${categoryId === cat.id ? 'bg-primary-50 text-primary-600 font-medium' : 'text-gray-600 hover:bg-gray-50'}`}
                                    >
                                        {cat.name}
                                    </button>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

                {/* Main Content */}
                <div className="flex-1">
                    {/* Search Bar */}
                    <div className="mb-6">
                        <form onSubmit={handleSearch} className="flex gap-2">
                            <input
                                type="text"
                                name="q"
                                defaultValue={search}
                                placeholder="Tìm kiếm văn bản..."
                                className="input"
                            />
                            <button type="submit" className="btn btn-primary">
                                Tìm kiếm
                            </button>
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
                                                    src={`http://localhost:5000${doc.thumbnail_url}`}
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
                                                    {doc.view_count} lượt xem
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
