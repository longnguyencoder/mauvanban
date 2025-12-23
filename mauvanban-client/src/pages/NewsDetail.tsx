import { useQuery } from '@tanstack/react-query';
import { useParams, Link } from 'react-router-dom';
import { newsApi } from '../api/news';
import SEO from '../components/common/SEO';
import { CalendarIcon, EyeIcon, ArrowLeftIcon, UserIcon } from '@heroicons/react/24/outline';
import { format } from 'date-fns';
import { vi } from 'date-fns/locale';

export default function NewsDetail() {
    const { slug } = useParams<{ slug: string }>();

    const { data: response, isLoading } = useQuery({
        queryKey: ['news-detail', slug],
        queryFn: () => newsApi.getBySlug(slug!),
        enabled: !!slug
    });

    if (isLoading) {
        return (
            <div className="max-w-4xl mx-auto px-4 py-12 animate-pulse">
                <div className="h-10 bg-gray-200 rounded w-3/4 mb-8" />
                <div className="h-6 bg-gray-200 rounded w-full mb-4" />
                <div className="h-6 bg-gray-200 rounded w-full mb-4" />
                <div className="h-96 bg-gray-200 rounded-2xl mb-8" />
                <div className="space-y-4">
                    <div className="h-4 bg-gray-200 rounded w-full" />
                    <div className="h-4 bg-gray-200 rounded w-5/6" />
                    <div className="h-4 bg-gray-200 rounded w-4/6" />
                </div>
            </div>
        );
    }

    const news = response?.data;

    if (!news) {
        return (
            <div className="text-center py-24">
                <h2 className="text-2xl font-bold text-gray-900">Không tìm thấy bài viết</h2>
                <Link to="/news" className="text-primary-600 mt-4 inline-block hover:underline">
                    Quay lại danh sách tin tức
                </Link>
            </div>
        );
    }

    // JSON-LD for Article
    const schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": news.title,
        "description": news.summary,
        "author": {
            "@type": "Person",
            "name": news.author
        },
        "datePublished": news.created_at,
        "image": news.thumbnail_url
    };

    return (
        <div className="min-h-screen bg-white pb-24">
            <SEO title={news.title} description={news.summary} schema={schema} />

            <div className="max-w-4xl mx-auto px-4 pt-12">
                <Link
                    to="/news"
                    className="inline-flex items-center text-sm text-gray-500 hover:text-primary-600 mb-8 transition-colors"
                >
                    <ArrowLeftIcon className="w-4 h-4 mr-2" />
                    Quay lại tin tức
                </Link>

                <header className="mb-12">
                    <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 mb-6 leading-tight">
                        {news.title}
                    </h1>

                    <div className="flex flex-wrap items-center gap-6 text-sm text-gray-500 border-y border-gray-100 py-6">
                        <div className="flex items-center">
                            <UserIcon className="w-5 h-5 mr-2 text-gray-400" />
                            <span className="font-medium text-gray-700">{news.author}</span>
                        </div>
                        <div className="flex items-center">
                            <CalendarIcon className="w-5 h-5 mr-2 text-gray-400" />
                            {format(new Date(news.created_at), "dd 'Tháng' M, yyyy", { locale: vi })}
                        </div>
                        <div className="flex items-center">
                            <EyeIcon className="w-5 h-5 mr-2 text-gray-400" />
                            {news.views_count} lượt xem
                        </div>
                    </div>
                </header>

                {news.thumbnail_url && (
                    <div className="relative h-96 md:h-[500px] mb-12 rounded-3xl overflow-hidden shadow-2xl">
                        <img
                            src={news.thumbnail_url}
                            alt={news.title}
                            className="w-full h-full object-cover"
                        />
                    </div>
                )}

                <div
                    className="prose prose-lg prose-primary max-w-none prose-headings:font-bold prose-headings:text-gray-900 prose-p:text-gray-700 prose-li:text-gray-700 prose-img:rounded-2xl"
                    dangerouslySetInnerHTML={{ __html: news.content }}
                />

                <div className="mt-16 pt-8 border-t border-gray-100 flex flex-col items-center">
                    <p className="text-gray-500 text-sm mb-4 italic">Cảm ơn bạn đã đọc bài viết!</p>
                    <div className="flex space-x-4">
                        <Link
                            to="/documents"
                            className="px-6 py-2 bg-primary-600 text-white rounded-full font-medium shadow-lg shadow-primary-200 hover:bg-primary-700 transition-all"
                        >
                            Khám phá Văn Bản
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
