import { create } from 'zustand';
import { authApi, User, LoginCredentials, RegisterData } from '../api/auth';

interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: string | null;

    login: (credentials: LoginCredentials) => Promise<void>;
    register: (data: RegisterData) => Promise<void>;
    logout: () => void;
    loadUser: () => Promise<void>;
    clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
    user: null,
    token: localStorage.getItem('access_token'),
    isAuthenticated: !!localStorage.getItem('access_token'),
    isLoading: false,
    error: null,

    login: async (credentials) => {
        try {
            set({ isLoading: true, error: null });
            const { data } = await authApi.login(credentials);

            const { user, access_token, refresh_token } = data.data;

            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', refresh_token);
            localStorage.setItem('user', JSON.stringify(user));

            set({
                user,
                token: access_token,
                isAuthenticated: true,
                isLoading: false,
            });
        } catch (error: any) {
            set({
                error: error.response?.data?.message || 'Login failed',
                isLoading: false,
            });
            throw error;
        }
    },

    register: async (data) => {
        try {
            set({ isLoading: true, error: null });
            await authApi.register(data);

            // After successful registration, automatically login
            const loginResponse = await authApi.login({
                email: data.email,
                password: data.password
            });

            const { user, access_token, refresh_token } = loginResponse.data.data;

            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', refresh_token);
            localStorage.setItem('user', JSON.stringify(user));

            set({
                user,
                token: access_token,
                isAuthenticated: true,
                isLoading: false,
            });
        } catch (error: any) {
            set({
                error: error.response?.data?.message || 'Registration failed',
                isLoading: false,
            });
            throw error;
        }
    },

    logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');

        set({
            user: null,
            token: null,
            isAuthenticated: false,
        });
    },

    loadUser: async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            set({ isAuthenticated: false });
            return;
        }

        try {
            const { data } = await authApi.getMe();
            set({
                user: data.data,
                isAuthenticated: true,
            });
        } catch (error) {
            set({
                user: null,
                token: null,
                isAuthenticated: false,
            });
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
        }
    },

    clearError: () => set({ error: null }),
}));
