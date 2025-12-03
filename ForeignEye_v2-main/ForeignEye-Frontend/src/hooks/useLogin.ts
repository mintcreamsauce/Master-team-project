import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/client';

interface LoginRequest {
  username: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  user?: {
    user_id: number;
    username: string;
    email?: string;
  };
}

async function loginUser(credentials: LoginRequest): Promise<LoginResponse> {
  const { data } = await apiClient.post<{ data: LoginResponse }>('/auth/login', credentials);
  return data.data;
}

export function useLogin() {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: loginUser,
    onSuccess: (data) => {
      // 1. 토큰을 localStorage에 저장
      localStorage.setItem('access_token', data.access_token);

      // 2. apiClient의 기본 헤더를 즉시 업데이트
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;

      console.log('✅ 로그인 성공:', data.user?.username);

      // 3. 기사 목록 페이지로 리디렉션
      navigate('/articles');
    },
    onError: (error: any) => {
      console.error('❌ 로그인 실패:', error.response?.data?.message || error.message);
    },
  });
}
