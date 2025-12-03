import { Flex, Button, Heading, Box } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';

function Header() {
  const navigate = useNavigate();

  return (
    <Flex 
      as="header" 
      position="fixed"
      top={0}
      left={0}
      right={0}
      bg="white"
      p={4}
      borderBottomWidth="1px"
      zIndex={100}
      align="center"
      shadow="sm"
    >
      <Heading 
        size="md" 
        color="blue.600"
        cursor="pointer"
        onClick={() => navigate('/')}
        _hover={{ color: 'blue.700' }}
      >
        ForeignEye
      </Heading>
      <Box flex="1" />
      <Box>
        <Button 
          onClick={() => navigate('/articles')} 
          variant="ghost" 
          mr={2}
        >
          기사 목록
        </Button>
        <Button 
          onClick={() => navigate('/my-collection')} 
          variant="ghost" 
          mr={2}
        >
          💎 내 수집
        </Button>
        <Button 
          onClick={() => navigate('/global-map')} 
          colorPalette="teal" 
          size="sm"
        >
          🗺️ 전체 지식 맵 (P5)
        </Button>
      </Box>
    </Flex>
  );
}

export default Header;
