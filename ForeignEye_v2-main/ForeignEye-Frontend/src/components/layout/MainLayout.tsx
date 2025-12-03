import { Box } from '@chakra-ui/react';
import { Outlet } from 'react-router-dom';
import Header from './Header';

function MainLayout() {
  return (
    <Box>
      <Header />
      {/* Header 높이만큼 여백을 줍니다 */}
      <Box pt="60px" minH="100vh" bg="gray.50"> 
        <Outlet /> {/* 현재 경로의 컴포넌트(HomePage, ArticleList 등)가 여기에 렌더링됩니다 */}
      </Box>
    </Box>
  );
}

export default MainLayout;
