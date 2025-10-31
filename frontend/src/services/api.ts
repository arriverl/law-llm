/**
 * API服务层
 */
import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { useAuthStore } from '../stores/authStore';

// API基础配置
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // 未授权，清除认证状态
      useAuthStore.getState().logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 认证相关API
export const authAPI = {
  login: (username: string, password: string) =>
    apiClient.post('/api/auth/login', { username, password }),
  
  register: (userData: {
    username: string;
    email: string;
    password: string;
    full_name?: string;
    role?: string;
  }) =>
    apiClient.post('/api/auth/register', userData),
  
  getCurrentUser: () =>
    apiClient.get('/api/auth/me'),
  
  refreshToken: () =>
    apiClient.post('/api/auth/refresh'),
  
  logout: () =>
    apiClient.post('/api/auth/logout'),
};

// 法律AI相关API
export const legalAIAPI = {
  consult: (question: string, context?: string, category?: string) =>
    apiClient.post('/api/legal-ai/consult', {
      question,
      context,
      category,
    }),
  
  analyze: (documentText: string, analysisType: string, jurisdiction?: string) =>
    apiClient.post('/api/legal-ai/analyze', {
      document_text: documentText,
      analysis_type: analysisType,
      jurisdiction,
    }),
  
  batchConsult: (questions: string[], batchId?: string) =>
    apiClient.post('/api/legal-ai/batch-consult', {
      questions,
      batch_id: batchId,
    }),
  
  getConsultations: (skip: number = 0, limit: number = 20) =>
    apiClient.get(`/api/legal-ai/consultations?skip=${skip}&limit=${limit}`),
  
  getCategories: () =>
    apiClient.get('/api/legal-ai/categories'),
  
  getModelStatus: () =>
    apiClient.get('/api/legal-ai/model-status'),
};

// 知识库相关API
export const knowledgeAPI = {
  getKnowledge: (category?: string, skip: number = 0, limit: number = 20) =>
    apiClient.get(`/api/knowledge?category=${category || ''}&skip=${skip}&limit=${limit}`),
  
  getKnowledgeById: (id: number) =>
    apiClient.get(`/api/knowledge/${id}`),
  
  createKnowledge: (knowledgeData: {
    title: string;
    content: string;
    category: string;
    tags: string[];
    source: string;
  }) =>
    apiClient.post('/api/knowledge', knowledgeData),
  
  updateKnowledge: (id: number, knowledgeData: {
    title?: string;
    content?: string;
    category?: string;
    tags?: string[];
    source?: string;
  }) =>
    apiClient.put(`/api/knowledge/${id}`, knowledgeData),
  
  deleteKnowledge: (id: number) =>
    apiClient.delete(`/api/knowledge/${id}`),
  
  searchKnowledge: (query: string, category?: string, tags?: string[], limit: number = 10) =>
    apiClient.post('/api/knowledge/search', {
      query,
      category,
      tags,
      limit,
    }),
  
  uploadFile: (file: File, category: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);
    return apiClient.post('/api/knowledge/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  getCategories: () =>
    apiClient.get('/api/knowledge/categories'),
  
  getStats: () =>
    apiClient.get('/api/knowledge/stats'),
};

// 生态管理相关API
export const ecosystemAPI = {
  getPartners: (partnerType?: string, region?: string, skip: number = 0, limit: number = 20) =>
    apiClient.get(`/api/ecosystem/partners?type=${partnerType || ''}&region=${region || ''}&skip=${skip}&limit=${limit}`),
  
  getPartner: (id: number) =>
    apiClient.get(`/api/ecosystem/partners/${id}`),
  
  createPartner: (partnerData: {
    name: string;
    type: string;
    region: string;
    contact_info: Record<string, any>;
    services: string[];
  }) =>
    apiClient.post('/api/ecosystem/partners', partnerData),
  
  updatePartner: (id: number, partnerData: {
    name: string;
    type: string;
    region: string;
    contact_info: Record<string, any>;
    services: string[];
  }) =>
    apiClient.put(`/api/ecosystem/partners/${id}`, partnerData),
  
  deletePartner: (id: number) =>
    apiClient.delete(`/api/ecosystem/partners/${id}`),
  
  deploySmartContract: (contractData: {
    contract_type: string;
    parties: string[];
    terms: Record<string, any>;
    jurisdiction: string;
  }) =>
    apiClient.post('/api/ecosystem/smart-contracts', contractData),
  
  initiateDataSharing: (sharingData: {
    partner_id: number;
    data_type: string;
    sharing_level: string;
    purpose: string;
  }) =>
    apiClient.post('/api/ecosystem/data-sharing', sharingData),
  
  getStats: () =>
    apiClient.get('/api/ecosystem/stats'),
  
  getRegions: () =>
    apiClient.get('/api/ecosystem/regions'),
};

// 数据分析相关API
export const analyticsAPI = {
  getOverview: () =>
    apiClient.get('/api/analytics/overview'),
  
  getConsultationAnalytics: (days: number = 30) =>
    apiClient.get(`/api/analytics/consultations?days=${days}`),
  
  getEcosystemAnalytics: () =>
    apiClient.get('/api/analytics/ecosystem'),
  
  getBusinessMetrics: () =>
    apiClient.get('/api/analytics/business'),
  
  getAIPerformance: () =>
    apiClient.get('/api/analytics/ai-performance'),
  
  exportData: (format: string = 'json', startDate?: string, endDate?: string) =>
    apiClient.get(`/api/analytics/export?format=${format}&start_date=${startDate || ''}&end_date=${endDate || ''}`),
};

export default apiClient;






