import { useQuery } from '@tanstack/react-query';
import apiClient from '../api/client';

// P5: React Flow 형식의 노드/엣지 타입
interface ReactFlowNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: any;
}

interface ReactFlowEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  animated?: boolean;
  style?: any;
}

interface KnowledgeMapResponse {
  nodes: ReactFlowNode[];
  edges: ReactFlowEdge[];
}

async function fetchKnowledgeMap(): Promise<KnowledgeMapResponse> {
  const { data } = await apiClient.get('/knowledge-map');
  return data.data; // API가 { data: { nodes: [], edges: [] } } 형식으로 반환
}

export function useKnowledgeMap() {
  return useQuery({
    queryKey: ['knowledge-map'],
    queryFn: fetchKnowledgeMap,
    staleTime: 1000 * 60,
  });
}
