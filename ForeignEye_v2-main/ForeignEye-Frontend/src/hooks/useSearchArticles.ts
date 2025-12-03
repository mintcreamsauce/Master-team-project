import { useQuery } from '@tanstack/react-query';
import apiClient from '../api/client';
import type { Article } from '../types';

async function fetchArticlesByConcept(conceptName: string): Promise<Article[]> {
  const { data } = await apiClient.get('/search/articles_by_concept', {
    params: { concept_name: conceptName },
  });
  return data.data.articles;
}

export function useSearchArticles(conceptName: string | null) {
  return useQuery({
    queryKey: ['articles', conceptName],
    queryFn: () => fetchArticlesByConcept(conceptName!),
    enabled: !!conceptName,
    staleTime: 1000 * 60 * 5,
  });
}
