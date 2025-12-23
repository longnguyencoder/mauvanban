import api from './axios';

export interface NewsArticle {
    id: string;
    title: string;
    slug: string;
    summary: string;
    content: string;
    thumbnail_url?: string;
    author: string;
    views_count: number;
    created_at: string;
}

export interface NewsPagination {
    total: number;
    pages: number;
    current_page: number;
    per_page: number;
    has_next: boolean;
    has_prev: boolean;
}

export const newsApi = {
    getAll: async (page = 1, per_page = 10) => {
        const { data } = await api.get(`/news?page=${page}&per_page=${per_page}`);
        return data;
    },

    getBySlug: async (slug: string) => {
        const { data } = await api.get(`/news/${slug}`);
        return data;
    },

    generate: async (topic: string, keywords: string) => {
        const { data } = await api.post('/news/generate', { topic, keywords });
        return data;
    },

    create: async (newsData: Partial<NewsArticle>) => {
        const { data } = await api.post('/news', newsData);
        return data;
    }
};
