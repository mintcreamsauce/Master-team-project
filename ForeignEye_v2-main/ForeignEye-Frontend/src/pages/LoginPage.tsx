import { useState } from 'react';
import { Box, Heading, VStack, Input, Button, Text, Flex } from '@chakra-ui/react';
import { useLogin } from '../hooks/useLogin';

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const loginMutation = useLogin();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loginMutation.mutate({ username, password });
  };

  return (
    <Flex h="100vh" justify="center" align="center" bg="gray.50">
      <Box w="400px" p={8} borderWidth={1} borderRadius="md" shadow="lg" bg="white">
        <form onSubmit={handleSubmit}>
          <VStack gap={4}>
            <Heading size="lg">ForeignEye 로그인</Heading>
            <Text fontSize="sm" color="gray.600">
              테스트 계정: testuser / test1234
            </Text>
            <Input 
              placeholder="사용자명" 
              value={username} 
              onChange={(e) => setUsername(e.target.value)}
              required
            />
            <Input 
              placeholder="비밀번호" 
              type="password"
              value={password} 
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <Button 
              type="submit" 
              colorScheme="blue" 
              w="full"
              disabled={loginMutation.isPending}
            >
              {loginMutation.isPending ? '로그인 중...' : '로그인'}
            </Button>
            {loginMutation.isError && (
              <Text color="red.500" fontSize="sm">
                로그인에 실패했습니다. 아이디와 비밀번호를 확인하세요.
              </Text>
            )}
          </VStack>
        </form>
      </Box>
    </Flex>
  );
}

export default LoginPage;
