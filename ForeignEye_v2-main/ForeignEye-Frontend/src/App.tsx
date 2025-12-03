import { Box } from '@chakra-ui/react';
import { Routes, Route } from 'react-router-dom';
import { ReactFlowProvider } from 'reactflow';

import MainLayout from './components/layout/MainLayout';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import ArticleListPage from './pages/ArticleListPage';
import ArticleDetailPage from './pages/ArticleDetailPage';
import GraphPage from './pages/GraphPage';
import GlobalMapPage from './pages/GlobalMapPage';
import MyCollectionPage from './pages/MyCollectionPage';

function App() {
  return (
    <Box w='100vw' h='100vh' bg='gray.50'>
      <ReactFlowProvider>
        <Routes>
          {/* MainLayout을 사용하는 페이지 (Header 포함) */}
          <Route element={<MainLayout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/articles" element={<ArticleListPage />} />
            <Route path="/articles/:articleId" element={<ArticleDetailPage />} />
            <Route path="/my-collection" element={<MyCollectionPage />} />
            <Route path="/global-map" element={<GlobalMapPage />} />
          </Route>
          
          {/* Header가 필요 없는 독립 페이지 */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/map/:conceptName" element={<GraphPage />} />
        </Routes>
      </ReactFlowProvider>
    </Box>
  );
}
export default App;
