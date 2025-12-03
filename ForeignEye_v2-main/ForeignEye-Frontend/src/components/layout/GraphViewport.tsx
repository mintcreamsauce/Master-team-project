import { useCallback, useState, useEffect, useRef } from 'react';
import { Box, Flex, Spinner } from '@chakra-ui/react';
import ReactFlow, {
  type Node, type Edge, Background, Controls, MiniMap,
  useNodesState, useEdgesState, addEdge, type Connection, type NodeTypes,
} from 'reactflow';
import 'reactflow/dist/style.css';
import MyConceptNode from '../nodes/MyConceptNode';
import ArticleNode from '../nodes/ArticleNode';
import RelativeNode from '../nodes/RelativeNode';
import ArticleDetailSidebar from './ArticleDetailSidebar';
import { useCollectConcept } from '../../hooks/useCollectConcept';
import { useSearchArticles } from '../../hooks/useSearchArticles';
import { useKnowledgeMap } from '../../hooks/useKnowledgeMap';
import type { Article, NodeData } from '../../types';

const nodeTypes: NodeTypes = {
  myConceptNode: MyConceptNode,
  articleNode: ArticleNode,
  relativeNode: RelativeNode,
};

function GraphViewport() {
  const [nodes, setNodes, onNodesChange] = useNodesState<NodeData>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
  const [searchConceptName, setSearchConceptName] = useState<string | null>(null);

  // P4 FIX: 레이스 컨디션 방지를 위한 ref
  const collectingNodeId = useRef<string | null>(null);

  const collectMutation = useCollectConcept();
  const { data: foundArticles, isLoading: isSearchLoading } = useSearchArticles(searchConceptName);
  const { data: knowledgeMap } = useKnowledgeMap();

  // 백엔드에서 실제 수집된 개념으로 초기 노드 생성
  useEffect(() => {
    if (knowledgeMap && nodes.length === 0) {
      const initialNodes: Node<NodeData>[] = knowledgeMap.graph.nodes
        .filter(gNode => gNode.is_collected)
        .map((gNode, index) => ({
          id: `concept-${gNode.id}`,
          type: 'myConceptNode' as const,
          position: { 
            x: 100 + (index % 3) * 300, 
            y: 150 + Math.floor(index / 3) * 200 
          },
          data: {
            type: 'myConceptNode' as const,
            concept: {
              concept_id: gNode.id,
              name: gNode.label,
              description_ko: gNode.description,
              real_world_examples_ko: gNode.real_world_examples,
              is_collected: gNode.is_collected,
            },
          },
        }));
      setNodes(initialNodes);
    }
  }, [knowledgeMap, nodes.length, setNodes]);

  // P4 FIX: mutation 완료 시 ref 해제
  useEffect(() => {
    if (!collectMutation.isPending) {
      collectingNodeId.current = null;
    }
  }, [collectMutation.isPending]);

  // P2: 기사 노드 중복 생성 방지
  useEffect(() => {
    if (foundArticles && searchConceptName) {
      const parentNode = nodes.find(n => n.data.concept?.name === searchConceptName);
      if (!parentNode) return;

      const existingNodeIds = new Set(nodes.map(n => n.id));
      const existingEdgeIds = new Set(edges.map(e => e.id));

      const newArticleNodes: Node<NodeData>[] = foundArticles
        .map((article, index) => ({
          id: `article-${article.article_id}`, type: 'articleNode' as const,
          position: {
            x: parentNode.position.x + 250,
            y: parentNode.position.y + (index * 100) - ((foundArticles.length - 1) * 50 / 2),
          },
          data: { type: 'articleNode' as const, article: article },
        }))
        .filter(n => !existingNodeIds.has(n.id));

      const newEdges: Edge[] = foundArticles
        .map(article => ({
          id: `edge-${parentNode.id}-article-${article.article_id}`,
          source: parentNode.id,
          target: `article-${article.article_id}`,
          animated: true,
        }))
        .filter(e => !existingEdgeIds.has(e.id));

      setNodes((nds) => [...nds, ...newArticleNodes]);
      setEdges((eds) => [...eds, ...newEdges]);
      setSearchConceptName(null);
    }
  }, [foundArticles, searchConceptName, nodes, edges, setNodes, setEdges]);

  const onConnect = useCallback((params: Connection) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  const handleRelativeNodeClick = useCallback(
    (node: Node<NodeData>) => {
      if (!node.data.relativeConcept) return;

      // P4 FIX: 현재 클릭한 노드가 "이미 처리 중"인지 확인
      if (collectingNodeId.current === node.id) {
        console.log(`⚠️ Request for ${node.id} is already in progress. Skipping.`);
        return;
      }

      // P4 FIX: 이미 파란색(myConceptNode)인지 확인
      if (node.type === 'myConceptNode') {
        console.log(`⚠️ Concept '${node.data.concept?.name}' is already collected. Skipping.`);
        return;
      }
      
      // P4 FIX: 같은 concept_id를 가진 파란색 노드가 이미 존재하는지 확인
      const conceptId = node.data.relativeConcept.concept_id;
      const conceptName = node.data.relativeConcept.name;
      const existingMyConceptNode = nodes.find(
        n => n.type === 'myConceptNode' && n.data.concept?.concept_id === conceptId
      );

      if (existingMyConceptNode) {
        console.log(`⚠️ Concept '${conceptName}' already exists. Removing duplicate gray node.`);
        setNodes((nds) => nds.filter(n => n.id !== node.id));
        setEdges((eds) => eds.filter(e => e.target === node.id));
        return;
      }
      
      // P4 FIX: "처리 중" 상태로 즉시 설정
      collectingNodeId.current = node.id;

      // 낙관적 업데이트: 회색 노드를 즉시 파란색으로 변환
      setNodes((nds) =>
        nds.map((n) =>
          n.id === node.id
            ? { ...n, type: 'myConceptNode' as const,
                data: {
                  type: 'myConceptNode' as const,
                  concept: {
                    concept_id: conceptId,
                    name: conceptName,
                    description_ko: '...', real_world_examples_ko: [], is_collected: true,
                  },
                },
              }
            : n
        )
      );

      // API 호출
      collectMutation.mutate({
        conceptId: conceptId,
        conceptName: conceptName,
      });
    },
    [collectMutation, setNodes, nodes, setEdges, collectingNodeId]
  );

  const handleArticleNodeClick = useCallback((article: Article, sourceNodeId: string) => {
    setSelectedArticle(article);
    const sourceNode = nodes.find(n => n.id === sourceNodeId);
    if (!sourceNode) return;

    // P3 FIX: 중복 노드 및 엣지 생성 방지
    const existingNodeIds = new Set(nodes.map(n => n.id));
    const existingEdgeIds = new Set(edges.map(e => e.id));
    
    const conceptsToAdd = article.relative_concepts.filter((concept) => {
      const nodeId = `relative-${article.article_id}-${concept.concept_id}`;
      const edgeId = `edge-${sourceNodeId}-relative-${concept.concept_id}`;
      return !existingNodeIds.has(nodeId) && !existingEdgeIds.has(edgeId);
    });
    
    if (conceptsToAdd.length === 0) {
      console.log(`⚠️ All relative concepts for article ${article.article_id} already exist. Skipping.`);
      return;
    }

    const newRelativeNodes: Node<NodeData>[] = conceptsToAdd.map((concept, index) => ({
      id: `relative-${article.article_id}-${concept.concept_id}`, type: 'relativeNode' as const,
      position: {
        x: sourceNode.position.x + 250,
        y: sourceNode.position.y + (index * 80) - ((conceptsToAdd.length - 1) * 40 / 2),
      },
      data: { type: 'relativeNode' as const, relativeConcept: concept },
    }));

    const newEdges: Edge[] = conceptsToAdd.map(concept => ({
      id: `edge-${sourceNodeId}-relative-${concept.concept_id}`,
      source: sourceNodeId,
      target: `relative-${article.article_id}-${concept.concept_id}`,
      style: { strokeDasharray: '5 5' },
    }));

    setNodes((nds) => [...nds, ...newRelativeNodes]);
    setEdges((eds) => [...eds, ...newEdges]);
  }, [nodes, edges, setNodes, setEdges, setSelectedArticle]);

  const handleMyConceptNodeClick = useCallback((conceptName: string) => {
    setSearchConceptName(conceptName);
  }, []);

  const onNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node<NodeData>) => {
      if (node.data.type === 'relativeNode' && node.data.relativeConcept) {
        handleRelativeNodeClick(node);
      } else if (node.data.type === 'articleNode' && node.data.article) {
        handleArticleNodeClick(node.data.article, node.id);
      } else if (node.data.type === 'myConceptNode' && node.data.concept) {
        handleMyConceptNodeClick(node.data.concept.name);
      }
    },
    [handleRelativeNodeClick, handleArticleNodeClick, handleMyConceptNodeClick]
  );

  return (
    <Flex w="100%" h="100%">
      <Box flex="1" position="relative">
        <ReactFlow
          nodes={nodes} edges={edges} onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange} onConnect={onConnect}
          onNodeClick={onNodeClick} nodeTypes={nodeTypes} fitView
        >
          <Background />
          <Controls />
          <MiniMap />
        </ReactFlow>
        {isSearchLoading && (
          <Spinner
            size="xl" position="absolute" top="50%" left="50%"
            transform="translate(-50%, -50%)" color="blue.500"
          />
        )}
      </Box>
      {selectedArticle && (
        <ArticleDetailSidebar
          article={selectedArticle}
          onClose={() => setSelectedArticle(null)}
        />
      )}
    </Flex>
  );
}
export default GraphViewport;
