import { useQuery } from '@tanstack/react-query';
import apiClient from '../api/client';
import type { Article } from '../types';

async function fetchArticleDetail(articleId: string): Promise<Article> {
  const { data } = await apiClient.get<{ data: Article }>(`/articles/${articleId}`);
  return data.data;
}

export function useArticleDetail(articleId: string | undefined) {
  return useQuery({
    queryKey: ['article', articleId],
    queryFn: () => fetchArticleDetail(articleId!),
    enabled: !!articleId, // articleId가 있을 때만 쿼리 실행
    staleTime: 1000 * 60 * 5, // 5분
  });
}
