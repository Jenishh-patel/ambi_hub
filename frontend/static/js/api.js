/**
 * API utility functions for Ambitious Hub
 */

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// API request wrapper
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
    };
    
    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers,
        },
    };
    
    try {
        const response = await fetch(url, mergedOptions);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API request error:', error);
        throw error;
    }
}

// API methods
const API = {
    // Accounts
    getProfile: () => apiRequest('/api/accounts/profile/'),
    getDashboardStats: () => apiRequest('/api/accounts/dashboard-stats/'),
    getLeaderboard: (limit = 100) => apiRequest(`/api/accounts/leaderboard/?limit=${limit}`),
    getFeed: () => apiRequest('/api/accounts/feed/'),
    
    // Solo
    getCategories: () => apiRequest('/api/solo/categories/'),
    createCategory: (data) => apiRequest('/api/solo/categories/', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
    getTasks: (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest(`/api/solo/tasks/${queryString ? '?' + queryString : ''}`);
    },
    createTask: (data) => apiRequest('/api/solo/tasks/', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
    completeTask: (taskId) => apiRequest(`/api/solo/tasks/${taskId}/complete/`, {
        method: 'POST',
    }),
    deleteTask: (taskId) => apiRequest(`/api/solo/tasks/${taskId}/`, {
        method: 'DELETE',
    }),
    getDailySummary: (date) => {
        const url = date ? `/api/solo/daily-summary/?date=${date}` : '/api/solo/daily-summary/';
        return apiRequest(url);
    },
    getMotivationalQuote: () => apiRequest('/api/solo/motivational-quote/'),
    
    // Clans
    getClans: (visibility = 'all') => apiRequest(`/api/clans/?visibility=${visibility}`),
    createClan: (data) => apiRequest('/api/clans/', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
    getClan: (clanId) => apiRequest(`/api/clans/${clanId}/`),
    joinClan: (clanId) => apiRequest(`/api/clans/${clanId}/join/`, {
        method: 'POST',
    }),
    getClanMembers: (clanId) => apiRequest(`/api/clans/${clanId}/members/`),
    getClanChallenges: (clanId) => apiRequest(`/api/clans/${clanId}/challenges/`),
    getClanLeaderboard: (clanId) => apiRequest(`/api/clans/${clanId}/leaderboard/`),
    getClanMessages: (clanId) => apiRequest(`/api/clans/${clanId}/messages/`),
    sendClanMessage: (clanId, content) => apiRequest(`/api/clans/${clanId}/messages/`, {
        method: 'POST',
        body: JSON.stringify({ content }),
    }),
    
    // Achievements
    getBadges: () => apiRequest('/api/achievements/badges/'),
    getMilestones: () => apiRequest('/api/achievements/milestones/'),
    getCertificate: (milestoneId) => apiRequest(`/api/achievements/certificate/${milestoneId}/`),
    
    // Analytics
    getDailyAnalytics: (date) => {
        const url = date ? `/api/analytics/daily/?date=${date}` : '/api/analytics/daily/';
        return apiRequest(url);
    },
    getWeeklyAnalytics: () => apiRequest('/api/analytics/weekly/'),
    getMonthlyAnalytics: () => apiRequest('/api/analytics/monthly/'),
    getXPTimeline: (days = 30) => apiRequest(`/api/analytics/xp-timeline/?days=${days}`),
    getCategoryTrends: (days = 30) => apiRequest(`/api/analytics/category-trends/?days=${days}`),
    exportPDF: (data) => apiRequest('/api/analytics/export-pdf/', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { API, getCookie };
}

