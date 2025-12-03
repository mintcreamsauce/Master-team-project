import { useEffect } from 'react';
import { Box, Flex, Spinner, Heading, Text, Stack } from '@chakra-ui/react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type NodeTypes,
} from 'reactflow';
import 'reactflow/dist/style.css';
import MyConceptNode from '../components/nodes/MyConceptNode';
import ArticleNode from '../components/nodes/ArticleNode';
import RelativeNode from '../components/nodes/RelativeNode';
import { useKnowledgeMap } from '../hooks/useKnowledgeMap';

// GraphPage와 동일한 nodeTypes
const nodeTypes: NodeTypes = {
  myConceptNode: MyConceptNode,
  articleNode: ArticleNode,
  relativeNode: RelativeNode,
};

function GlobalMapPage() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // P5 API 훅 호출
  const { data: graphData, isLoading, error } = useKnowledgeMap();

  // API가 데이터를 가져오면 nodes/edges 상태를 업데이트
  useEffect(() => {
    if (graphData?.nodes && graphData?.edges) {
      setNodes(graphData.nodes);
      setEdges(graphData.edges);
    }
  }, [graphData, setNodes, setEdges]);

  // 로딩 중
  if (isLoading) {
    return (
      <Flex w="100%" h="100vh" align="center" justify="center">
        <Stack gap={4} align="center">
          <Spinner size="xl" color="blue.500" />
          <Text fontSize="lg" color="gray.600">
            전체 지식 맵을 불러오는 중...
          </Text>
        </Stack>
      </Flex>
    );
  }

  // 오류 발생
  if (error) {
    return (
      <Flex w="100%" h="100vh" align="center" justify="center">
        <Stack gap={4} align="center">
          <Heading size="lg" color="red.500">
            오류가 발생했습니다
          </Heading>
          <Text color="gray.600">
            {error instanceof Error ? error.message : '알 수 없는 오류'}
          </Text>
        </Stack>
      </Flex>
    );
  }

  // 데이터가 없을 때
  if (!graphData || nodes.length === 0) {
    return (
      <Flex w="100%" h="100vh" align="center" justify="center">
        <Stack gap={4} align="center">
          <Heading size="lg" color="gray.500">
            수집한 개념이 없습니다
          </Heading>
          <Text color="gray.600">
            기사를 읽고 개념을 수집해보세요!
          </Text>
        </Stack>
      </Flex>
    );
  }

  return (
    <Flex w="100%" h="100vh" flexDirection="column">
      {/* 헤더 */}
      <Box bg="white" borderBottom="1px" borderColor="gray.200" px={6} py={4}>
        <Heading size="md" color="gray.700">
          📚 전체 지식 맵
        </Heading>
        <Text fontSize="sm" color="gray.500" mt={1}>
          {nodes.length}개의 개념 · {edges.length}개의 연결
        </Text>
      </Box>

      {/* React Flow 캔버스 */}
      <Box flex="1" position="relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          defaultEdgeOptions={{
            animated: true,
            style: { stroke: '#6366f1', strokeWidth: 2 },
            labelStyle: { fill: '#4b5563', fontWeight: 600, fontSize: 12 },
            labelBgStyle: { fill: '#ffffff', fillOpacity: 0.9 },
          }}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.1}
          maxZoom={2}
        >
          <Background />
          <Controls />
          <MiniMap
            nodeColor={(node) => {
              return node.type === 'myConceptNode' ? '#4299E1' : '#E2E8F0';
            }}
          />
        </ReactFlow>
      </Box>
    </Flex>
  );
}

export default GlobalMapPage;
