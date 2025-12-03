export interface RelativeConcept {
  concept_id: number; name: string; relation_type?: string; strength: number;
}
export interface Article {
  article_id: number; title: string; title_ko?: string; content_preview?: string;
  url: string; original_url?: string; summary_ko?: string; created_at: string; 
  relative_concepts: RelativeConcept[];
  concept_count?: number;
  preview_concepts?: { concept_id: number; name: string }[];
  concepts?: Concept[]; // 기사의 모든 개념 목록 (ArticleDetailPage용)
}
export interface Concept {
  concept_id: number; name: string; description_ko: string;
  real_world_examples_ko: string[]; is_collected?: boolean;
}
export interface GraphNode {
  id: number; label: string; description: string;
  real_world_examples: string[]; is_primary?: boolean;
  is_collected: boolean; shape: string; size: number;
}
export interface GraphEdge {
  from: number; to: number; relation_type?: string; strength: number; width: number;
}
export interface KnowledgeMap {
  graph: { nodes: GraphNode[]; edges: GraphEdge[]; };
}
export type NodeType = 'myConceptNode' | 'articleNode' | 'relativeNode';
export interface NodeData {
  type: NodeType;
  concept?: Concept;
  article?: Article;
  relativeConcept?: RelativeConcept;
}