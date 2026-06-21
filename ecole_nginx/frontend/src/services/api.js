import axios from 'axios';

const api = axios.create({
    baseURL: 'https://aplekol360.local/api/v1',
    headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
});

// Ajoute automatiquement le token JWT s'il existe
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default api;