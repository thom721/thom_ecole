const api = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_URL,
  withCredentials: true,
})

// Intercepteur : cache les détails dans la console
api.interceptors.response.use(
  response => response,
  error => {
    console.error(`[API Error] ${error.response?.status}`) // ← pas d'URL
    return Promise.reject(error)
  }
)

export default api

// location /api/ {
//     # Bloquer si le header Origin n'est pas le bon
//     if ($http_origin !~* "institutionlemignon.com") {
//         return 403;
//     }
//     proxy_pass http://127.0.0.1:8000;
// }

// "https://institutionlemignon.com",
//         "https://admin.institutionlemignon.com",