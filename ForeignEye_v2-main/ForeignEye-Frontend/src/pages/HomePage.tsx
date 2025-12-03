import { Button, Heading, Text, Stack } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';

function HomePage() {
  const navigate = useNavigate();

  return (
    <Stack 
      justify="center" 
      align="center" 
      minH="calc(100vh - 60px)" 
      pt={4} 
      gap={10}
    >
      <Stack gap={2} align="center">
        <Heading size="xl" color="blue.700">
          ForeignEye
        </Heading>
        <Text fontSize="lg" color="gray.600">
          AI 분석 기반 지식 탐험 플랫폼
        </Text>
      </Stack>
      
      <Stack 
        gap={4} 
        p={8} 
        borderWidth="1px" 
        borderRadius="lg" 
        bg="white" 
        maxW="500px"
        w="full"
        shadow="md"
      >
        <Text fontWeight="bold" fontSize="md" textAlign="center">
          P1~P4 게임 루프 시작하기
        </Text>
        
        <Button 
          size="lg" 
          colorPalette="blue"
          onClick={() => navigate('/articles')}
          w="full"
        >
          📄 기사 목록에서 탐험 시작
        </Button>

        <Button 
          size="lg" 
          variant="outline"
          colorPalette="teal"
          onClick={() => navigate('/global-map')}
          w="full"
        >
          🗺️ 내 전체 지식 맵 보기 (P5)
        </Button>

        <Button 
          size="sm" 
          variant="ghost"
          onClick={() => navigate('/login')}
        >
          (관리자 로그인)
        </Button>
      </Stack>
    </Stack>
  );
}

export default HomePage;
