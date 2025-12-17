import api from './axios';
import { Category } from './categories';

export interface Document {
    id: string; // Changed to string UUID
    code: string;
    title: string;
    slug: string;
    description: string;
    content?: string;
    file_url?: string;
    file_type: string;
    thumbnail_url?: string;
    price: number;
    views_count: number;
    downloads_count: number;
    created_at: string;
    category?: Category;
    category_id?: number | string;
    is_featured?: boolean;
}

export interface DocumentListResponse {
    success: boolean;
    data: {
        items: Document[];
        documents: Document[];
        total: number;
        page: number;
        pages: number;
        per_page: number;
    };
}

export interface DocumentParams {
    page?: number;
    per_page?: number;
    q?: string;
    category_id?: number | string;
    sort?: string;
    min_price?: number;
    max_price?: number;
}

export const documentsApi = {
    getAll: (params?: DocumentParams) =>
        api.get<DocumentListResponse>('/documents', { params }),

    getById: (id: number | string) =>
        api.get<{ success: boolean; data: Document }>(`/documents/${id}`),

    getBySlug: (slug: string) =>
        api.get<{ success: boolean; data: Document }>(`/documents/${slug}`),

    download: (id: number | string) =>
        api.post<{ success: boolean; data: { download_url: string } }>(`/documents/${id}/download`),

    // Admin methods
    update: (id: number | string, data: any) =>
        api.put<{ success: boolean; data: Document }>(`/admin/documents/${id}`, data),

    delete: (id: number | string) =>
        api.delete<{ success: boolean }>(`/admin/documents/${id}`),
};
