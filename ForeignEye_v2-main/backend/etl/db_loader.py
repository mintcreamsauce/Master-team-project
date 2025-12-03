"""
데이터베이스 적재기

Discovery 단계에서 추출한 개념을 기사와 연결합니다.
"""

from typing import Dict, Optional, List

from app.extensions import db
from app.models import Article, Concept, Article_Concept, Concept_Relation
from etl.neo4j_client import neo4j_conn


PLACEHOLDER_DESCRIPTION = "(Placeholder) 기사에서 이 개념이 어떻게 사용되는지 확인하세요."


class DBLoader:
    """간소화된 데이터베이스 적재 클래스"""

    def __init__(self, app_context):
        self.app_context = app_context

    def load_article_data(self, article_data: Dict, analysis: Dict) -> Optional[Article]:
        """기사와 개념을 저장하고 연결합니다."""
        with self.app_context:
            try:
                # Stale State 방지: 세션 캐시 무효화
                db.session.expire_all()
                
                url = article_data['url']
                existing_article = Article.query.filter_by(original_url=url).first()
                if existing_article:
                    print(f"  ⊘ Article already exists (ID: {existing_article.article_id})")
                    return None

                new_article = Article(
                    title=article_data['title'],
                    title_ko=analysis.get('title_ko', ''),
                    original_url=url,
                    summary_ko=analysis.get('summary_ko', '')
                )
                db.session.add(new_article)
                db.session.flush()

                print(f"  ✓ Created Article (ID: {new_article.article_id})")

                concept_names = analysis.get('concept_names', [])
                if not concept_names:
                    print("  ! No concepts detected by AI.")
                    db.session.commit()
                    return new_article

                linked_count = 0
                for concept_name in concept_names:
                    concept = self._get_or_create_concept(concept_name)
                    if concept and self._link_concept_to_article(new_article, concept):
                        linked_count += 1

                db.session.commit()
                print(f"  ✓ Linked {linked_count} concepts to article")
                print(f"  ✓✓ Successfully saved article to database!")
                return new_article

            except Exception as e:
                db.session.rollback()
                print(f"  ✗✗ Database error: {e}")
                import traceback
                traceback.print_exc()
                return None

    def _get_or_create_concept(self, concept_name: str) -> Optional[Concept]:
        cleaned_name = (concept_name or '').strip()
        if not cleaned_name:
            return None

        # Stale State 방지: 최신 데이터 조회
        db.session.expire_all()
        
        concept = Concept.query.filter_by(name=cleaned_name).first()
        if concept:
            return concept

        concept = Concept(
            name=cleaned_name,
            description_ko=PLACEHOLDER_DESCRIPTION,
            real_world_examples_ko=[]
        )
        db.session.add(concept)
        db.session.flush()
        print(f"  ✓ Created concept: {cleaned_name} (ID: {concept.concept_id})")

        # Neo4j에도 노드 생성 (ETL 1단계)
        try:
            neo4j_conn.execute_query(
                f"MERGE (c:Concept {{name: '{cleaned_name}'}})"
            )
            print(f"  ✓ (Neo4j) Created node: {cleaned_name}")
        except Exception as e:
            print(f"  ✗ (Neo4j) Error creating node: {e}")
        
        return concept

    def _link_concept_to_article(self, article: Article, concept: Concept) -> bool:
        # Stale State 방지: 최신 데이터 조회
        db.session.expire_all()
        
        existing_link = Article_Concept.query.filter_by(
            article_id=article.article_id,
            concept_id=concept.concept_id
        ).first()

        if existing_link:
            return False

        db.session.add(Article_Concept(
            article_id=article.article_id,
            concept_id=concept.concept_id
        ))
        return True
    
    def load_concept_relations(self, relations: List[Dict]) -> int:
        """
        개념 간 관계를 데이터베이스에 저장합니다.
        
        Args:
            relations (List[Dict]): 관계 목록. 각 항목은 {'from': str, 'to': str, 'relation_type': str} 형태
            
        Returns:
            int: 저장된 관계 수
        """
        with self.app_context:
            try:
                # Stale State 방지: 이전 세션의 모든 변경사항을 먼저 커밋
                db.session.commit()
                # 세션 캐시 무효화 (신선한 데이터 조회 보장)
                db.session.expire_all()
                
                saved_count = 0
                skipped_count = 0
                error_count = 0
                
                print(f"\n  ⟳ Processing {len(relations)} relations...")
                print(f"  ✓ Session committed and cache cleared (Stale State prevention)")
                
                for rel in relations:
                    from_name = rel.get('from', '').strip()
                    to_name = rel.get('to', '').strip()
                    relation_type = rel.get('relation_type', '').strip()
                    
                    if not all([from_name, to_name, relation_type]):
                        error_count += 1
                        continue
                    
                    # from 개념 조회
                    from_concept = Concept.query.filter_by(name=from_name).first()
                    if not from_concept:
                        print(f"  ! Concept not found: {from_name}")
                        error_count += 1
                        continue
                    
                    # to 개념 조회
                    to_concept = Concept.query.filter_by(name=to_name).first()
                    if not to_concept:
                        print(f"  ! Concept not found: {to_name}")
                        error_count += 1
                        continue
                    
                    # 중복 관계 확인 (Stale State 방지: 매번 최신 데이터 조회)
                    db.session.expire_all()
                    existing_relation = Concept_Relation.query.filter_by(
                        from_concept_id=from_concept.concept_id,
                        to_concept_id=to_concept.concept_id
                    ).first()
                    
                    if existing_relation:
                        skipped_count += 1
                        continue
                    
                    # 1. MySQL에 관계 저장
                    new_relation = Concept_Relation(
                        from_concept_id=from_concept.concept_id,
                        to_concept_id=to_concept.concept_id,
                        relation_type=relation_type,
                        strength=5  # Default strength
                    )
                    db.session.add(new_relation)
                    
                    # 2. Neo4j에 관계 저장 (ETL 2단계)
                    try:
                        neo4j_conn.execute_query(
                            f"""
                            MATCH (c1:Concept {{name: '{from_name}'}})
                            MATCH (c2:Concept {{name: '{to_name}'}})
                            MERGE (c1)-[r:{relation_type} {{strength: 5}}]->(c2)
                            """
                        )
                        print(f"  ✓ (Neo4j) Linked: {from_name} -> {to_name}")
                    except Exception as e:
                        print(f"  ✗ (Neo4j) Error linking relations: {e}")
                    
                    saved_count += 1
                    
                    if saved_count % 10 == 0:
                        print(f"  → Processed {saved_count} relations...")
                
                # 최종 커밋
                db.session.commit()
                
                print(f"\n  ✓ Relation loading complete!")
                print(f"  ✓ Saved: {saved_count} relations")
                print(f"  ⊘ Skipped (duplicates): {skipped_count} relations")
                print(f"  ✗ Errors: {error_count} relations")
                
                return saved_count
            
            except Exception as e:
                db.session.rollback()
                print(f"  ✗✗ Database error while loading relations: {e}")
                import traceback
                traceback.print_exc()
                return 0
