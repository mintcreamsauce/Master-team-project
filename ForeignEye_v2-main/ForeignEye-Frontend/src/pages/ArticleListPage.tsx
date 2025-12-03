import { Box, Heading, VStack, Text, Spinner, Flex, Badge, Button } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { useArticles } from '../hooks/useArticles';

function ArticleListPage() {
  const { data: articles, isLoading, isError } = useArticles();
  const navigate = useNavigate();

  if (isLoading) {
    return (
      <Spinner 
        size="xl" 
        position="absolute" 
        top="50%" 
        left="50%" 
        transform="translate(-50%, -50%)"
      />
    );
  }

  if (isError) {
    return (
      <Box p={8} textAlign="center">
        <Text color="red.500">기사를 불러오는 데 실패했습니다.</Text>
      </Box>
    );
  }

  return (
    <Box p={8} maxW="1000px" mx="auto">
      <Flex justify="space-between" align="center" mb={6}>
        <Heading>AI가 분석한 기사 목록</Heading>
        <Button
          colorPalette="blue"
          onClick={() => navigate('/global-map')}
          size="lg"
        >
          📚 전체 지식 맵 보기
        </Button>
      </Flex>
      <VStack gap={4} align="stretch">
        {articles?.map((article) => (
          <Box 
            key={article.article_id} 
            p={4} 
            borderWidth={1} 
            borderRadius="md" 
            shadow="sm"
            bg="white"
          >
            <Heading 
              size="md" 
              mb={2}
              onClick={() => navigate(`/articles/${article.article_id}`)}
              _hover={{ textDecoration: 'underline', color: 'blue.600' }}
              cursor="pointer"
            >
              {article.title_ko || article.title}
            </Heading>
            <Text fontSize="sm" color="gray.600" lineClamp={2} mb={3}>
              {article.summary_ko}
            </Text>
            <Flex wrap="wrap" gap={2}>
              {article.preview_concepts?.map((concept) => (
                <Badge 
                  key={concept.concept_id}
                  onClick={() => navigate(`/map/${encodeURIComponent(concept.name)}`)}
                  colorPalette="purple"
                  cursor="pointer"
                  _hover={{ bg: 'purple.100' }}
                >
                  {concept.name}
                </Badge>
              ))}
            </Flex>
          </Box>
        ))}
      </VStack>
    </Box>
  );
}

export default ArticleListPage;
