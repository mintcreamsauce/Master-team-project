import { memo } from 'react';
import { Handle, Position, type NodeProps } from 'reactflow';
import { Box, Text } from '@chakra-ui/react';
import type { NodeData } from '../../types';

function RelativeNode({ data }: NodeProps<NodeData>) {
  return (
    <Box
      bg='gray.100' color='gray.700' px={3} py={2} borderRadius='md'
      borderWidth={2} borderColor='gray.300' borderStyle='dashed'
      opacity={0.7} minW='100px' textAlign='center' cursor='pointer'
      _hover={{ opacity: 1, borderColor: 'gray.500' }}
    >
      <Text fontSize='sm' fontWeight='medium'>
        {data.relativeConcept?.name || '친척 개념'}
      </Text>
      <Handle type='target' position={Position.Left} />
    </Box>
  );
}
export default memo(RelativeNode);
