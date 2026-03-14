/**
 * Authentication service for managing user authentication and tokens.
 */

const API_BASE_URL = '';
const TOKEN_KEY = 'carbonsense_token';

export const authService = {
    /**
     * Register a new user
     */
    async register(email, password, fullName) {
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email,
                password,
                full_name: fullName
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }

        return await response.json();
    },

    /**
     * Login user and store token
     */
    async login(email, password) {
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }

        const data = await response.json();
        localStorage.setItem(TOKEN_KEY, data.access_token);
        return data;
    },

    /**
     * Logout user and clear token
     */
    logout() {
        localStorage.removeItem(TOKEN_KEY);
    },

    /**
     * Get current user info
     */
    async getCurrentUser() {
        const token = this.getToken();
        if (!token) return null;

        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                this.logout();
                return null;
            }

            return await response.json();
        } catch (error) {
            console.error('Get current user error:', error);
            this.logout();
            return null;
        }
    },

    /**
     * Update user profile
     */
    async updateProfile(fullName, password) {
        const token = this.getToken();
        if (!token) throw new Error('Not authenticated');

        const body = {};
        if (fullName) body.full_name = fullName;
        if (password) body.password = password;

        const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Update failed');
        }

        return await response.json();
    },

    /**
     * Delete user account
     */
    async deleteAccount() {
        const token = this.getToken();
        if (!token) throw new Error('Not authenticated');

        const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Delete failed');
        }

        this.logout();
    },

    /**
     * Get stored token
     */
    getToken() {
        return localStorage.getItem(TOKEN_KEY);
    },

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!this.getToken();
    }
};
