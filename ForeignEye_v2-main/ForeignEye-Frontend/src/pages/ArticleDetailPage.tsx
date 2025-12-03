import { Box, Heading, VStack, Text, Spinner, Flex, Badge, Link } from '@chakra-ui/react';
import { useParams, useNavigate } from 'react-router-dom';
import { useArticleDetail } from '../hooks/useArticleDetail';

function ArticleDetailPage() {
  const { articleId } = useParams<{ articleId: string }>();
  const { data: article, isLoading, isError } = useArticleDetail(articleId);
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

  if (isError || !article) {
    return (
      <Box p={8} textAlign="center">
        <Text color="red.500">기사 상세 정보를 불러오는 데 실패했습니다.</Text>
      </Box>
    );
  }

  return (
    <Box p={8} maxW="1000px" mx="auto">
      <Heading size="xl" mb={4}>
        {article.title_ko || article.title}
      </Heading>
      
      <VStack gap={6} align="stretch">
        {/* AI 요약 섹션 */}
        <Box p={5} borderWidth={1} borderRadius="md" shadow="sm" bg="white">
          <Heading size="md" mb={3}>AI 요약</Heading>
          <Text fontSize="md" color="gray.700" whiteSpace="pre-wrap">
            {article.summary_ko || article.content_preview || "요약 정보가 없습니다."}
          </Text>
          
          {/* 원문 보기 링크 */}
          {(article.original_url || article.url) && (
            <Link 
              href={article.original_url || article.url} 
              target="_blank" 
              color="blue.500" 
              fontWeight="bold" 
              mt={4} 
              display="block"
            >
              🔗 원본 기사 읽기
            </Link>
          )}
        </Box>

        {/* 모든 연관 개념 섹션 */}
        <Box p={5} borderWidth={1} borderRadius="md" shadow="sm" bg="white">
          <Heading size="md" mb={3}>
            이 기사의 모든 연관 개념 ({article.concepts?.length || 0}개)
          </Heading>
          <Flex wrap="wrap" gap={2}>
            {article.concepts?.map((concept) => (
              <Badge 
                key={concept.concept_id}
                colorPalette="purple"
                cursor="pointer"
                _hover={{ bg: 'purple.100' }}
                onClick={() => navigate(`/map/${encodeURIComponent(concept.name)}`)}
              >
                {concept.name}
              </Badge>
            ))}
          </Flex>
          {(!article.concepts || article.concepts.length === 0) && (
            <Text color="gray.500">연관 개념이 없습니다.</Text>
          )}
        </Box>
      </VStack>
    </Box>
  );
}

export default ArticleDetailPage;
