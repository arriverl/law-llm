import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, theme } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { QueryClient, QueryClientProvider } from 'react-query';

// 页面组件
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import LegalConsultation from './pages/LegalConsultation';
import KnowledgeBase from './pages/KnowledgeBase';
import Ecosystem from './pages/Ecosystem';
import Analytics from './pages/Analytics';
import Profile from './pages/Profile';

// 状态管理
import { useAuthStore } from './stores/authStore';

// 样式
import './App.css';

// React Query 客户端
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const App: React.FC = () => {
  const { isAuthenticated } = useAuthStore();

  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider
        locale={zhCN}
        theme={{
          algorithm: theme.defaultAlgorithm,
          token: {
            colorPrimary: '#1890ff',
            borderRadius: 6,
          },
        }}
      >
        <Router>
          <div className="App">
            <Routes>
              {/* 公开路由 */}
              <Route 
                path="/login" 
                element={!isAuthenticated ? <Login /> : <Navigate to="/dashboard" replace />} 
              />
              
              {/* 受保护的路由 */}
              <Route 
                path="/*" 
                element={
                  isAuthenticated ? (
                    <Layout>
                      <Routes>
                        <Route path="/" element={<Navigate to="/dashboard" replace />} />
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/consultation" element={<LegalConsultation />} />
                        <Route path="/knowledge" element={<KnowledgeBase />} />
                        <Route path="/ecosystem" element={<Ecosystem />} />
                        <Route path="/analytics" element={<Analytics />} />
                        <Route path="/profile" element={<Profile />} />
                      </Routes>
                    </Layout>
                  ) : (
                    <Navigate to="/login" replace />
                  )
                } 
              />
            </Routes>
          </div>
        </Router>
      </ConfigProvider>
    </QueryClientProvider>
  );
};

export default App;






