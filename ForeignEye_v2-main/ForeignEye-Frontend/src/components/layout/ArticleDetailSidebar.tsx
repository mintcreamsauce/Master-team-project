import {
  Drawer, Heading, Text, Link, VStack, Badge, Flex
} from '@chakra-ui/react';
import type { Article } from '../../types';

interface Props {
  article: Article;
  onClose: () => void;
}

function ArticleDetailSidebar({ article, onClose }: Props) {
  return (
    <Drawer.Root open={true} placement='end' onOpenChange={(e) => !e.open && onClose()} size='md'>
      <Drawer.Backdrop />
      <Drawer.Positioner>
        <Drawer.Content>
          <Drawer.Header borderBottomWidth='1px'>
            <Drawer.Title>{article.title_ko || article.title}</Drawer.Title>
            <Drawer.CloseTrigger />
          </Drawer.Header>
          <Drawer.Body>
            <VStack gap={4} alignItems='start'>
              <Heading size='sm'>요약 (Preview)</Heading>
              <Text fontSize='md'>{article.content_preview || '미리보기 없음'}</Text>
              <Link href={article.url} target='_blank' color='blue.500' fontWeight='bold'>
                원본 기사 읽기
              </Link>
              <Heading size='sm'>연관된 '친척 개념' (P3)</Heading>
              <Flex wrap='wrap' gap={2}>
                {article.relative_concepts.map((concept, index) => (
                  <Badge key={`${concept.concept_id}-${index}`} size='lg' colorPalette='teal'>
                    {concept.name}
                  </Badge>
                ))}
              </Flex>
              <Text fontSize='xs' color='gray.500'>
                (M1(캡스톤)에서는 백엔드가 P3 방어를 위해 최대 10개까지 제공합니다)
              </Text>
            </VStack>
          </Drawer.Body>
        </Drawer.Content>
      </Drawer.Positioner>
    </Drawer.Root>
  );
}
export default ArticleDetailSidebar;
