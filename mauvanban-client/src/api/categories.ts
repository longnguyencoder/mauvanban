import api from './axios';

export interface Category {
    id: string; // Changed to string (UUID)
    name: string;
    slug: string;
    description?: string;
    icon?: string;
    parent_id?: string | null; // Changed to string
    children?: Category[];
    document_count?: number;
}

export const categoriesApi = {
    getTree: () =>
        api.get<{ success: boolean; data: Category[] }>('/categories/tree'),

    getAll: () =>
        api.get<{ success: boolean; data: Category[] }>('/categories'),

    getBySlug: (slug: string) =>
        api.get<{ success: boolean; data: Category }>('/categories/' + slug),

    getById: (id: string) =>
        api.get<{ success: boolean; data: Category }>(`/admin/categories/${id}`),

    // Admin
    create: (data: Partial<Category>) =>
        api.post<{ success: boolean; data: Category }>('/admin/categories', data),

    update: (id: number | string, data: Partial<Category>) =>
        api.put<{ success: boolean; data: Category }>(`/admin/categories/${id}`, data),

    delete: (id: number | string) =>
        api.delete<{ success: boolean; message: string }>(`/admin/categories/${id}`),
};
