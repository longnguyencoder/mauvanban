import api from './axios';

export interface User {
    id: string;
    full_name: string;
    email: string;
    phone_number?: string;
    role: 'admin' | 'user';
    balance: number;
    is_active: boolean;
    created_at: string;
}

export interface UserListResponse {
    success: boolean;
    data: {
        users: User[];
        total: number;
        page: number;
        per_page: number;
        pages: number;
    };
}

export interface UserParams {
    page?: number;
    per_page?: number;
    role?: string;
    is_active?: boolean;
}

export const usersApi = {
    getAll: (params?: UserParams) =>
        api.get<UserListResponse>('/admin/users', { params }),

    getById: (id: string) =>
        api.get<{ success: boolean; data: User }>(`/admin/users/${id}`),

    create: (data: any) =>
        api.post<{ success: boolean; data: User }>('/admin/users', data),

    update: (id: string, data: any) =>
        api.put<{ success: boolean; data: User }>(`/admin/users/${id}`, data),

    delete: (id: string) =>
        api.delete<{ success: boolean }>(`/admin/users/${id}`),

    toggleActive: (id: string) =>
        api.put<{ success: boolean; data: User }>(`/admin/users/${id}/toggle-active`),

    adjustBalance: (id: string, amount: number) =>
        api.put<{ success: boolean; data: User }>(`/admin/users/${id}/balance`, { amount }),

    // User Profile
    updateProfile: (data: any) =>
        api.put<{ success: boolean; data: User }>('/auth/profile', data)
};
