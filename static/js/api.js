/**
 * API Client for Emotion Tracker Backend
 * Handles all HTTP requests to the backend API
 */

const API_BASE_URL = '/api/v1';

/**
 * Get authentication token from localStorage
 */
function getAuthToken() {
    return localStorage.getItem('access_token');
}

/**
 * Set authentication token in localStorage
 */
function setAuthToken(token) {
    localStorage.setItem('access_token', token);
}

/**
 * Remove authentication token from localStorage
 */
function removeAuthToken() {
    localStorage.removeItem('access_token');
}

/**
 * Check if user is authenticated
 */
function isAuthenticated() {
    return !!getAuthToken();
}

/**
 * Make an authenticated API request
 * @param {string} endpoint - API endpoint (without base URL)
 * @param {object} options - Fetch options
 * @returns {Promise<any>} - Response data
 */
async function apiRequest(endpoint, options = {}) {
    const token = getAuthToken();
    
    const defaultHeaders = {
        'Content-Type': 'application/json',
    };
    
    if (token) {
        defaultHeaders['Authorization'] = `Bearer ${token}`;
    }
    
    const config = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...(options.headers || {}),
        },
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        
        // Handle 401 Unauthorized - redirect to login
        if (response.status === 401) {
            removeAuthToken();
            window.location.href = 'login.html';
            throw new Error('Unauthorized');
        }
        
        // Handle errors
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        
        // Handle 204 No Content
        if (response.status === 204) {
            return null;
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Request failed:', error);
        throw error;
    }
}

/**
 * Auth API calls
 */
const AuthAPI = {
    /**
     * Register a new user
     * @param {string} email 
     * @param {string} password 
     * @returns {Promise<{access_token: string, token_type: string}>}
     */
    async register(email, password) {
        const response = await apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
        if (response.access_token) {
            setAuthToken(response.access_token);
        }
        return response;
    },
    
    /**
     * Login user
     * @param {string} email 
     * @param {string} password 
     * @returns {Promise<{access_token: string, token_type: string}>}
     */
    async login(email, password) {
        const response = await apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
        if (response.access_token) {
            setAuthToken(response.access_token);
        }
        return response;
    },
    
    /**
     * Logout user (client-side only)
     */
    logout() {
        removeAuthToken();
        window.location.href = 'login.html';
    },
    
    /**
     * Refresh access token
     * @param {string} refreshToken 
     * @returns {Promise<{access_token: string, token_type: string}>}
     */
    async refresh(refreshToken) {
        const response = await apiRequest('/auth/refresh', {
            method: 'POST',
            body: JSON.stringify({ refresh_token: refreshToken }),
        });
        if (response.access_token) {
            setAuthToken(response.access_token);
        }
        return response;
    },
};

/**
 * Emotions API calls
 */
const EmotionsAPI = {
    /**
     * Create a new emotion record
     * @param {object} data - Emotion data
     * @returns {Promise<object>}
     */
    async create(data) {
        return await apiRequest('/emotions/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },
    
    /**
     * Get today's emotion record
     * @returns {Promise<object>}
     */
    async getToday() {
        return await apiRequest('/emotions/today');
    },
    
    /**
     * Get emotion history
     * @param {object} params - Query parameters
     * @returns {Promise<object>}
     */
    async getHistory(params = {}) {
        const queryParams = new URLSearchParams();
        if (params.start_date) queryParams.append('start_date', params.start_date);
        if (params.end_date) queryParams.append('end_date', params.end_date);
        if (params.limit) queryParams.append('limit', params.limit);
        
        const query = queryParams.toString();
        const url = query ? `/emotions/?${query}` : '/emotions/';
        return await apiRequest(url);
    },
    
    /**
     * Update an emotion record
     * @param {string} emotionId - UUID of the emotion record
     * @param {object} data - Updated data
     * @returns {Promise<object>}
     */
    async update(emotionId, data) {
        return await apiRequest(`/emotions/${emotionId}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },
    
    /**
     * Delete an emotion record
     * @param {string} emotionId - UUID of the emotion record
     * @returns {Promise<object>}
     */
    async delete(emotionId) {
        return await apiRequest(`/emotions/${emotionId}`, {
            method: 'DELETE',
        });
    },
};

/**
 * Users API calls
 */
const UsersAPI = {
    /**
     * Get current user profile
     * @returns {Promise<object>}
     */
    async getProfile() {
        return await apiRequest('/users/me');
    },
    
    /**
     * Update current user profile
     * @param {object} data - Updated profile data
     * @returns {Promise<object>}
     */
    async updateProfile(data) {
        return await apiRequest('/users/me', {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },
    
    /**
     * Delete current user account
     * @returns {Promise<object>}
     */
    async deleteAccount() {
        return await apiRequest('/users/me', {
            method: 'DELETE',
        });
    },
    
    /**
     * Get user settings
     * @returns {Promise<object>}
     */
    async getSettings() {
        return await apiRequest('/users/me/settings');
    },
    
    /**
     * Update user settings
     * @param {object} data - Updated settings data
     * @returns {Promise<object>}
     */
    async updateSettings(data) {
        return await apiRequest('/users/me/settings', {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },
    
    /**
     * Add a hobby
     * @param {string} hobby - Hobby name
     * @returns {Promise<object>}
     */
    async addHobby(hobby) {
        return await apiRequest('/users/me/settings/hobbies', {
            method: 'POST',
            body: JSON.stringify({ hobby }),
        });
    },
    
    /**
     * Remove a hobby
     * @param {string} hobby - Hobby name
     * @returns {Promise<null>}
     */
    async removeHobby(hobby) {
        return await apiRequest(`/users/me/settings/hobbies/${encodeURIComponent(hobby)}`, {
            method: 'DELETE',
        });
    },
    
    /**
     * Add a coping method
     * @param {string} method - Coping method name
     * @returns {Promise<object>}
     */
    async addCopingMethod(method) {
        return await apiRequest('/users/me/settings/coping-methods', {
            method: 'POST',
            body: JSON.stringify({ method }),
        });
    },
    
    /**
     * Remove a coping method
     * @param {string} method - Coping method name
     * @returns {Promise<null>}
     */
    async removeCopingMethod(method) {
        return await apiRequest(`/users/me/settings/coping-methods/${encodeURIComponent(method)}`, {
            method: 'DELETE',
        });
    },
};

/**
 * Notifications API calls
 */
const NotificationsAPI = {
    /**
     * Update notification preferences
     * @param {object} data - Preferences data
     * @returns {Promise<object>}
     */
    async updatePreferences(data) {
        return await apiRequest('/notifications/preferences', {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },
    
    /**
     * Get notification history
     * @param {object} params - Query parameters
     * @returns {Promise<object>}
     */
    async getHistory(params = {}) {
        const queryParams = new URLSearchParams();
        if (params.skip) queryParams.append('skip', params.skip);
        if (params.limit) queryParams.append('limit', params.limit);
        if (params.unread_only) queryParams.append('unread_only', params.unread_only);
        
        const query = queryParams.toString();
        const url = query ? `/notifications?${query}` : '/notifications';
        return await apiRequest(url);
    },
    
    /**
     * Send a test notification
     * @returns {Promise<object>}
     */
    async sendTest() {
        return await apiRequest('/notifications/test', {
            method: 'POST',
        });
    },
};

// Export all APIs
window.API = {
    auth: AuthAPI,
    emotions: EmotionsAPI,
    users: UsersAPI,
    notifications: NotificationsAPI,
    // Utility functions
    getAuthToken,
    setAuthToken,
    removeAuthToken,
    isAuthenticated,
};
