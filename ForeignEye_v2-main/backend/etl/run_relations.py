"""
ETL Phase 2: 개념 관계 분석 및 저장 스크립트

기존 Concept 테이블의 개념들 간의 관계를 AI로 분석하여
Concept_Relation 테이블에 저장합니다.

사용법:
    python -m etl.run_relations
    
또는:
    from etl.run_relations import run_relations_etl
    run_relations_etl()
"""

import os
from dotenv import load_dotenv
from flask import current_app

from app import create_app
from app.extensions import db
from app.models import Concept
from etl.ai_analyzer import AIAnalyzer
from etl.db_loader import DBLoader


def run_relations_etl():
    """
    개념 관계 ETL 파이프라인 실행
    
    Returns:
        dict: {
            'total_concepts': int,
            'relations_saved': int
        }
    """
    print("=" * 70)
    print("ETL Phase 2: Concept Relations Pipeline")
    print("=" * 70)
    print()
    
    # Step 1: DB에서 모든 개념 로드
    print("STEP 1: Loading concepts from database...")
    print("-" * 70)
    
    try:
        concepts = Concept.query.all()
        
        if not concepts:
            print("\n✗ No concepts found in database.")
            print("   Please run 'python -m etl.run' first to populate concepts.")
            return {'total_concepts': 0, 'relations_saved': 0}
        
        concept_names = [c.name for c in concepts]
        print(f"✓ Loaded {len(concept_names)} concepts from database")
        print(f"  Concepts: {', '.join(concept_names[:10])}")
        if len(concept_names) > 10:
            print(f"  ... and {len(concept_names) - 10} more")
        
    except Exception as e:
        print(f"\n✗ Failed to load concepts from database: {e}")
        return {'total_concepts': 0, 'relations_saved': 0}
    
    print()
    
    # Step 2: AI 분석기 및 DB 로더 초기화
    print("STEP 2: Initializing AI analyzer and DB loader...")
    print("-" * 70)
    
    try:
        analyzer = AIAnalyzer()
        loader = DBLoader(current_app.app_context())
        print("✓ Components initialized successfully")
    except Exception as e:
        print(f"\n✗ Failed to initialize components: {e}")
        return {'total_concepts': len(concept_names), 'relations_saved': 0}
    
    print()
    
    # Step 3: AI에게 관계 분석 요청
    print("STEP 3: Analyzing concept relations with AI...")
    print("-" * 70)
    
    try:
        print(f"Requesting AI to analyze {len(concept_names)} concepts...")
        print("This may take a minute...")
        
        analysis = analyzer.analyze_concept_relations(concept_names)
        
        if not analysis:
            print("\n✗ AI analysis failed or returned no results.")
            return {'total_concepts': len(concept_names), 'relations_saved': 0}
        
        relations = analysis.get('relations', [])
        
        if not relations:
            print("\n✗ No relations found by AI.")
            return {'total_concepts': len(concept_names), 'relations_saved': 0}
        
        print(f"✓ AI analysis complete!")
        print(f"✓ Found {len(relations)} potential relations")
        
        # 샘플 관계 출력
        print("\nSample relations:")
        for i, rel in enumerate(relations[:5], 1):
            print(f"  {i}. {rel['from']} --[{rel['relation_type']}]--> {rel['to']}")
        if len(relations) > 5:
            print(f"  ... and {len(relations) - 5} more")
        
    except Exception as e:
        print(f"\n✗ Error during AI analysis: {e}")
        import traceback
        traceback.print_exc()
        return {'total_concepts': len(concept_names), 'relations_saved': 0}
    
    print()
    
    # Step 4: DB에 관계 저장
    print("STEP 4: Saving relations to database...")
    print("-" * 70)
    
    try:
        saved_count = loader.load_concept_relations(relations)
        
        if saved_count > 0:
            print(f"\n✓✓ Successfully saved {saved_count} relations to database!")
        else:
            print("\n⊘ No new relations were saved (all might be duplicates).")
        
    except Exception as e:
        print(f"\n✗✗ Error saving relations: {e}")
        import traceback
        traceback.print_exc()
        return {'total_concepts': len(concept_names), 'relations_saved': 0}
    
    # 최종 요약
    print()
    print("=" * 70)
    print("ETL Phase 2 Complete")
    print("=" * 70)
    print(f"✓ Total concepts analyzed: {len(concept_names)}")
    print(f"✓ Relations discovered: {len(relations)}")
    print(f"✓ Relations saved to DB: {saved_count}")
    print("=" * 70)
    
    return {
        'total_concepts': len(concept_names),
        'relations_saved': saved_count
    }


if __name__ == "__main__":
    load_dotenv()
    
    print("[App Context] Creating Flask app context...")
    config_name = os.getenv('FLASK_ENV', 'development')
    app = create_app(config_name)
    
    with app.app_context():
        print("[App Context] Flask app context created. Starting ETL Phase 2...")
        result = run_relations_etl()
        print("[App Context] ETL Phase 2 complete. DB commit guaranteed.")
        
        # 결과 출력
        if result['relations_saved'] > 0:
            print(f"\n✅ SUCCESS: {result['relations_saved']} concept relations saved!")
        else:
            print(f"\n⚠️  WARNING: No relations saved. Check logs above.")
