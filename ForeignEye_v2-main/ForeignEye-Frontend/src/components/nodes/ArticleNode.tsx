import { memo } from 'react';
import { Handle, Position, type NodeProps } from 'reactflow';
import { Box, Text, Icon } from '@chakra-ui/react';
import { FiFileText } from 'react-icons/fi';
import type { NodeData } from '../../types';

function ArticleNode({ data }: NodeProps<NodeData>) {
  return (
    <Box
      bg='white' px={3} py={2} borderRadius='md' borderWidth={2}
      borderColor='green.400' boxShadow='md' minW='120px' maxW='180px'
      cursor='pointer' _hover={{ borderColor: 'green.600', boxShadow: 'lg' }}
    >
      <Box display='flex' alignItems='center' gap={2}>
        <Icon as={FiFileText} color='green.500' />
         <Text fontSize='sm' fontWeight='semibold' lineClamp={2}>
          {data.article?.title_ko || data.article?.title || '기사'}
        </Text>
      </Box>
      <Handle type='source' position={Position.Right} />
      <Handle type='target' position={Position.Left} />
    </Box>
  );
}
export default memo(ArticleNode);
