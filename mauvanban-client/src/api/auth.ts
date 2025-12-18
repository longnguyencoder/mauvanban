import api from './axios';

export interface LoginCredentials {
    email: string;
    password: string;
}

export interface RegisterData {
    email: string;
    password: string;
    full_name?: string;
    phone?: string;
}

export interface User {
    id: string;
    email: string;
    full_name?: string;
    phone?: string;
    phone_number?: string;  // Added for compatibility
    role: string;
    balance: number;
    is_active: boolean;
    created_at?: string;    // Added for profile display
}

export interface AuthResponse {
    success: boolean;
    message: string;
    data: {
        user: User;
        access_token: string;
        refresh_token: string;
    };
}

export const authApi = {
    login: (credentials: LoginCredentials) =>
        api.post<AuthResponse>('/auth/login', credentials),

    register: (data: RegisterData) =>
        api.post<AuthResponse>('/auth/register', data),

    getMe: () =>
        api.get<{ success: boolean; data: User }>('/auth/me'),

    updateProfile: (data: { full_name?: string; phone?: string }) =>
        api.put('/auth/profile', data),

    changePassword: (data: { old_password: string; new_password: string }) =>
        api.post('/auth/change-password', data),
};
