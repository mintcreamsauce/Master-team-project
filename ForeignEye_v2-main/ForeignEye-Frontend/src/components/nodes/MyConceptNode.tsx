import { memo } from 'react';
import { Handle, Position, type NodeProps } from 'reactflow';
import { Box, Text } from '@chakra-ui/react';
import type { NodeData } from '../../types';

function MyConceptNode({ data }: NodeProps<NodeData>) {
  return (
    <Box
      bg='blue.500' color='white' px={4} py={3} borderRadius='lg'
      borderWidth={3} borderColor='blue.700' boxShadow='lg'
      minW='150px' textAlign='center' cursor='pointer'
      _hover={{ bg: 'blue.600' }}
    >
      <Text fontWeight='bold' fontSize='md'>
        {data.concept?.name || '내 개념'}
      </Text>
      <Handle type='source' position={Position.Right} />
      <Handle type='target' position={Position.Left} />
    </Box>
  );
}
export default memo(MyConceptNode);