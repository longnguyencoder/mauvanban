import { useQuery } from '@tanstack/react-query';
import { Link, useSearchParams } from 'react-router-dom';
import { newsApi, NewsArticle } from '../api/news';
import { CalendarIcon, EyeIcon } from '@heroicons/react/24/outline';
import { format } from 'date-fns';
import { vi } from 'date-fns/locale';

export default function NewsList() {
    const [searchParams] = useSearchParams();
    const page = parseInt(searchParams.get('page') || '1');

    const { data, isLoading } = useQuery({
        queryKey: ['news', page],
        queryFn: () => newsApi.getAll(page, 12)
    });

    if (isLoading) {
        return (
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {[1, 2, 3, 4, 5, 6].map((n) => (
                        <div key={n} className="bg-white rounded-2xl shadow-sm overflow-hidden animate-pulse">
                            <div className="h-48 bg-gray-200" />
                            <div className="p-6">
                                <div className="h-6 bg-gray-200 rounded w-3/4 mb-4" />
                                <div className="h-4 bg-gray-200 rounded w-full mb-2" />
                                <div className="h-4 bg-gray-200 rounded w-5/6" />
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    const news: NewsArticle[] = data?.data || [];

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="mb-12">
                <h1 className="text-3xl font-bold text-gray-900 mb-4">Tin tức & Kinh nghiệm</h1>
                <p className="text-lg text-gray-600">Những hướng dẫn, kinh nghiệm và tin tức mới nhất về thủ tục hành chính.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {news.map((item) => (
                    <Link
                        key={item.id}
                        to={`/news/${item.slug}`}
                        className="bg-white rounded-2xl shadow-sm overflow-hidden hover:shadow-md transition-shadow duration-300 border border-transparent hover:border-primary-100 flex flex-col h-full"
                    >
                        <div className="h-48 overflow-hidden bg-gray-100">
                            {item.thumbnail_url ? (
                                <img
                                    src={item.thumbnail_url}
                                    alt={item.title}
                                    className="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
                                />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center text-gray-300">
                                    <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                    </svg>
                                </div>
                            )}
                        </div>
                        <div className="p-6 flex flex-col flex-grow">
                            <div className="flex items-center space-x-4 text-xs text-gray-500 mb-3">
                                <span className="flex items-center">
                                    <CalendarIcon className="w-4 h-4 mr-1" />
                                    {format(new Date(item.created_at), 'dd MMM yyyy', { locale: vi })}
                                </span>
                                <span className="flex items-center">
                                    <EyeIcon className="w-4 h-4 mr-1" />
                                    {item.views_count}
                                </span>
                            </div>
                            <h2 className="text-xl font-bold text-gray-900 mb-3 line-clamp-2 hover:text-primary-600 transition-colors">
                                {item.title}
                            </h2>
                            <p className="text-gray-600 text-sm line-clamp-3 mb-4">
                                {item.summary}
                            </p>
                            <div className="mt-auto pt-4 flex items-center text-primary-600 font-semibold text-sm">
                                Xem chi tiết
                                <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                </svg>
                            </div>
                        </div>
                    </Link>
                ))}
            </div>

            {news.length === 0 && (
                <div className="text-center py-24">
                    <p className="text-gray-500 text-lg italic">Chưa có bài viết nào được đăng.</p>
                </div>
            )}
        </div>
    );
}
