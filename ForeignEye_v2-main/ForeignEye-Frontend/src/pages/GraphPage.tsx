import { useCallback, useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { Box, Flex, Spinner } from '@chakra-ui/react';
import ReactFlow, {
  type Node, type Edge, Background, Controls, MiniMap,
  useNodesState, useEdgesState, addEdge, type Connection, type NodeTypes,
} from 'reactflow';
import 'reactflow/dist/style.css';
import MyConceptNode from '../components/nodes/MyConceptNode';
import ArticleNode from '../components/nodes/ArticleNode';
import RelativeNode from '../components/nodes/RelativeNode';
import ArticleDetailSidebar from '../components/layout/ArticleDetailSidebar';
import { useCollectConcept } from '../hooks/useCollectConcept';
import { useSearchArticles } from '../hooks/useSearchArticles';
import type { Article, NodeData } from '../types';

const nodeTypes: NodeTypes = {
  myConceptNode: MyConceptNode,
  articleNode: ArticleNode,
  relativeNode: RelativeNode,
};

function GraphPage() {
  // URL에서 :conceptName 가져오기
  const { conceptName: urlConceptName } = useParams<{ conceptName: string }>();

  // 초기 노드를 URL에서 가져온 개념으로 설정
  const getInitialNodes = (): Node<NodeData>[] => {
    if (!urlConceptName) return [];
    return [{
      id: `concept-${urlConceptName}`,
      type: 'myConceptNode',
      position: { x: 100, y: 150 },
      data: {
        type: 'myConceptNode',
        concept: {
          concept_id: 0, // ID는 알 수 없으므로 0
          name: decodeURIComponent(urlConceptName),
          description_ko: '...',
          real_world_examples_ko: [],
          is_collected: true,
        },
      },
    }];
  };

  const [nodes, setNodes, onNodesChange] = useNodesState<NodeData>(getInitialNodes());
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
  const [searchConceptName, setSearchConceptName] = useState<string | null>(
    urlConceptName ? decodeURIComponent(urlConceptName) : null
  );

  // P4 FIX: 레이스 컨디션 방지를 위한 ref
  const collectingNodeId = useRef<string | null>(null);

  const collectMutation = useCollectConcept();
  const { data: foundArticles, isLoading: isSearchLoading } = useSearchArticles(searchConceptName);

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

      const conceptId = node.data.relativeConcept.concept_id;
      const conceptName = node.data.relativeConcept.name;

      // P4 FIX 강화: 함수형 업데이트로 최신 상태 확인
      setNodes((currentNodes) => {
        // 1. 현재 클릭한 노드가 이미 처리 중인지 확인
        if (collectingNodeId.current === node.id) {
          console.log(`⚠️ Request for ${node.id} is already in progress. Skipping.`);
          return currentNodes;
        }

        // 2. 클릭한 노드가 이미 파란색인지 확인
        const clickedNode = currentNodes.find(n => n.id === node.id);
        if (clickedNode?.type === 'myConceptNode') {
          console.log(`⚠️ Concept '${conceptName}' is already collected (type check). Skipping.`);
          return currentNodes;
        }

        // 3. 같은 concept_id를 가진 파란색 노드가 이미 존재하는지 확인
        const existingMyConceptNode = currentNodes.find(
          n => n.type === 'myConceptNode' && n.data.concept?.concept_id === conceptId
        );

        if (existingMyConceptNode) {
          console.log(`⚠️ Concept '${conceptName}' already exists (ID: ${conceptId}). Removing duplicate gray node.`);
          // 중복 회색 노드 제거
          setEdges((eds) => eds.filter(e => e.target !== node.id));
          return currentNodes.filter(n => n.id !== node.id);
        }

        // 4. "처리 중" 상태로 설정
        collectingNodeId.current = node.id;

        // 5. 낙관적 업데이트: 회색 노드를 즉시 파란색으로 변환
        const updatedNodes = currentNodes.map((n) =>
          n.id === node.id
            ? {
                ...n,
                type: 'myConceptNode' as const,
                data: {
                  type: 'myConceptNode' as const,
                  concept: {
                    concept_id: conceptId,
                    name: conceptName,
                    description_ko: '...',
                    real_world_examples_ko: [],
                    is_collected: true,
                  },
                },
              }
            : n
        );

        // 6. API 호출 (비동기)
        collectMutation.mutate({
          conceptId: conceptId,
          conceptName: conceptName,
        });

        return updatedNodes;
      });
    },
    [collectMutation, setNodes, setEdges]
  );

  const handleArticleNodeClick = useCallback((article: Article, sourceNodeId: string) => {
    setSelectedArticle(article);

    // P3 FIX 강화: 함수형 업데이트로 최신 상태 확인
    setNodes((currentNodes) => {
      const sourceNode = currentNodes.find(n => n.id === sourceNodeId);
      if (!sourceNode) {
        console.log(`⚠️ Source node ${sourceNodeId} not found. Skipping.`);
        return currentNodes;
      }

      // 현재 노드 ID 목록
      const existingNodeIds = new Set(currentNodes.map(n => n.id));

      // 추가할 개념 필터링 (중복 제거)
      const conceptsToAdd = article.relative_concepts.filter((concept) => {
        const nodeId = `relative-${article.article_id}-${concept.concept_id}`;
        return !existingNodeIds.has(nodeId);
      });

      if (conceptsToAdd.length === 0) {
        console.log(`⚠️ All relative concepts for article ${article.article_id} already exist. Skipping.`);
        return currentNodes;
      }

      // 새 회색 노드 생성
      const newRelativeNodes: Node<NodeData>[] = conceptsToAdd.map((concept, index) => ({
        id: `relative-${article.article_id}-${concept.concept_id}`,
        type: 'relativeNode' as const,
        position: {
          x: sourceNode.position.x + 250,
          y: sourceNode.position.y + (index * 80) - ((conceptsToAdd.length - 1) * 40 / 2),
        },
        data: { type: 'relativeNode' as const, relativeConcept: concept },
      }));

      // 엣지도 함수형 업데이트로 추가
      setEdges((currentEdges) => {
        const existingEdgeIds = new Set(currentEdges.map(e => e.id));

        const newEdges: Edge[] = conceptsToAdd
          .map(concept => ({
            id: `edge-${sourceNodeId}-relative-${concept.concept_id}`,
            source: sourceNodeId,
            target: `relative-${article.article_id}-${concept.concept_id}`,
            style: { strokeDasharray: '5 5' },
          }))
          .filter(edge => !existingEdgeIds.has(edge.id));

        if (newEdges.length === 0) {
          console.log(`⚠️ All edges for article ${article.article_id} already exist. Skipping.`);
          return currentEdges;
        }

        console.log(`✅ Adding ${newEdges.length} new edges for article ${article.article_id}`);
        return [...currentEdges, ...newEdges];
      });

      console.log(`✅ Adding ${newRelativeNodes.length} new relative nodes for article ${article.article_id}`);
      return [...currentNodes, ...newRelativeNodes];
    });
  }, [setNodes, setEdges, setSelectedArticle]);

  const handleMyConceptNodeClick = useCallback((conceptName: string) => {
    if (isSearchLoading) return;
    setSearchConceptName(conceptName);
  }, [isSearchLoading]);

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

export default GraphPage;
