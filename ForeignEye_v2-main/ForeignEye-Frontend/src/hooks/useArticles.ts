// [수정됨] src/hooks/useArticles.ts

import { useQuery } from '@tanstack/react-query';
import apiClient from '../api/client';
import type { Article } from '../types'; // ⬅️ Article 타입에 preview_concepts가 포함되어 있어야 합니다.

// 1. Windsurf님이 정의했던 "ArticlesResponse" 타입이 맞았습니다.
interface ArticlesResponse {
  items: Article[];
  // ... (기타 페이지네이션 정보)
}

async function fetchArticles(): Promise<Article[]> {
  // 2. [수정] 백엔드는 { data: { items: [...] } } 객체를 반환합니다.
  const { data } = await apiClient.get<{ data: ArticlesResponse }>('/articles');
  
  // 3. [수정] 따라서 .map()을 쓸 수 있는 "배열"인 'data.data.items'를 반환해야 합니다.
  return data.data.items; 
}

export function useArticles() {
  return useQuery({
    queryKey: ['articles'],
    queryFn: fetchArticles,
    staleTime: 1000 * 60 * 5, // 5분
  });
}