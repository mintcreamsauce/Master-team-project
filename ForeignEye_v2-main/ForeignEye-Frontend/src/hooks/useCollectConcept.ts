// [수정됨] src/hooks/useCollectConcept.ts
// useToast 관련 모든 코드를 제거합니다.

import { useMutation, useQueryClient } from '@tanstack/react-query';
// 1. (제거) import { useToast } from '@chakra-ui/react';
import apiClient from '../api/client';

// (toast.ts, createToaster 등 모든 관련 코드 불필요)

interface CollectConceptPayload {
  conceptId: number;
  conceptName: string; 
}

async function collectConcept({ conceptId }: CollectConceptPayload) {
  const { data } = await apiClient.post('/collections/concepts', {
    concept_id: conceptId,
  });
  return data.data;
}

export function useCollectConcept() {
  const queryClient = useQueryClient();
  // 2. (제거) const toast = useToast(); 

  return useMutation({
    mutationFn: collectConcept,
    onSuccess: (data, variables) => {
      // 3. (대체) 토스트 대신 "console.log"로 성공 피드백을 줍니다.
      console.log(
        `✅ P4 수집 성공: '${variables.conceptName}'`,
        data.message
      );
      queryClient.invalidateQueries({ queryKey: ['knowledge-map'] });
    },
    onError: (_error: any, variables) => {
      // 4. (대체) 토스트 대신 "console.error"로 실패 피드백을 줍니다.
      console.error(
        `❌ P4 수집 실패: '${variables.conceptName}'`,
        _error.response?.data?.message || '개념 수집 중 오류가 발생했습니다.'
      );
    },
  });
}