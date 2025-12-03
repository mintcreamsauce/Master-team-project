import { useQuery } from '@tanstack/react-query';
import apiClient from '../api/client';
import type { Concept } from '../types';

async function fetchMyCollection(): Promise<Concept[]> {
  const { data } = await apiClient.get<{ data: Concept[] }>('/collections/concepts');
  return data.data;
}

export function useMyCollection() {
  return useQuery({
    queryKey: ['my-collection'],
    queryFn: fetchMyCollection,
    staleTime: 1000 * 60, // 1분
  });
}
