import { Box, Heading, Text, Spinner, Flex, Badge, Stack } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { useMyCollection } from '../hooks/useMyCollection';

function MyCollectionPage() {
  const { data: concepts, isLoading, isError } = useMyCollection();
  const navigate = useNavigate();

  if (isLoading) {
    return (
      <Flex w="100%" h="100vh" align="center" justify="center">
        <Stack gap={4} align="center">
          <Spinner size="xl" color="blue.500" />
          <Text fontSize="lg" color="gray.600">
            수집한 개념을 불러오는 중...
          </Text>
        </Stack>
      </Flex>
    );
  }

  if (isError) {
    return (
      <Box p={8} textAlign="center">
        <Text color="red.500">수집한 개념을 불러오는 데 실패했습니다.</Text>
      </Box>
    );
  }

  return (
    <Box p={8} maxW="1000px" mx="auto">
      <Heading mb={6}>💎 내가 수집한 개념</Heading>
      
      {!concepts || concepts.length === 0 ? (
        <Box p={8} textAlign="center" borderWidth={1} borderRadius="md" bg="gray.50">
          <Text fontSize="lg" color="gray.600">
            아직 수집한 개념이 없습니다.
          </Text>
          <Text fontSize="sm" color="gray.500" mt={2}>
            기사를 읽고 흥미로운 개념을 수집해보세요!
          </Text>
        </Box>
      ) : (
        <>
          <Text fontSize="md" color="gray.600" mb={4}>
            총 {concepts.length}개의 개념을 수집했습니다
          </Text>
          
          <Stack gap={3}>
            {concepts.map((concept) => (
              <Box
                key={concept.concept_id}
                p={4}
                borderWidth={1}
                borderRadius="md"
                bg="white"
                shadow="sm"
                cursor="pointer"
                _hover={{ shadow: 'md', borderColor: 'blue.300' }}
                onClick={() => navigate(`/map/${encodeURIComponent(concept.name)}`)}
              >
                <Flex align="center" gap={3}>
                  <Badge colorPalette="blue" fontSize="md">
                    {concept.name}
                  </Badge>
                  {concept.description_ko && (
                    <Text fontSize="sm" color="gray.600" flex="1">
                      {concept.description_ko}
                    </Text>
                  )}
                </Flex>
              </Box>
            ))}
          </Stack>
        </>
      )}
    </Box>
  );
}

export default MyCollectionPage;
