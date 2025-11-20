import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_V1 = `${API_URL}/api/v1`;

// Configurar axios
const api = axios.create({
  baseURL: API_V1,
});

// Interceptor para adicionar token a todas as requisições
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para tratar erros de autenticação
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado ou inválido
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Casos
export const casesAPI = {
  list: (params) => api.get('/cases', { params }),
  get: (id) => api.get(`/cases/${id}`),
  create: (data) => api.post('/cases', data),
  update: (id, data) => api.put(`/cases/${id}`, data),
  classify: (id, data) => api.post(`/cases/${id}/classify`, data),
  updateStatus: (id, data) => api.post(`/cases/${id}/status`, data),
  getMyCases: () => api.get('/cases/my/cases'),
};

// Apontamentos
export const timeEntriesAPI = {
  list: (params) => api.get('/time-entries', { params }),
  get: (id) => api.get(`/time-entries/${id}`),
  create: (data) => api.post('/time-entries', data),
  update: (id, data) => api.put(`/time-entries/${id}`, data),
  delete: (id) => api.delete(`/time-entries/${id}`),
  getMy: () => api.get('/time-entries/my'),
};

// Sprints
export const sprintsAPI = {
  list: (params) => api.get('/sprints', { params }),
  get: (id) => api.get(`/sprints/${id}`),
  create: (data) => api.post('/sprints', data),
  update: (id, data) => api.put(`/sprints/${id}`, data),
  delete: (id) => api.delete(`/sprints/${id}`),
  addCases: (id, caseIds) => api.post(`/sprints/${id}/cases`, { case_ids: caseIds }),
  removeCase: (sprintId, caseId) => api.delete(`/sprints/${sprintId}/cases/${caseId}`),
  complete: (id) => api.post(`/sprints/${id}/complete`),
};

export default api;
