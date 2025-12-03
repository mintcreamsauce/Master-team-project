"""
ETL 파이프라인 실행 스크립트

뉴스 수집, 분석, 데이터베이스 적재를 수행합니다.

사용법:
    python -m etl.run
    
또는:
    from etl.run import run_etl_pipeline
    run_etl_pipeline()
"""

import os
from dotenv import load_dotenv
from flask import current_app

from app import create_app
from etl.gnews_fetcher import GNewsFetcher
from etl.web_scraper import WebScraper
from etl.ai_analyzer import AIAnalyzer
from etl.db_loader import DBLoader


def check_environment():
    """환경 변수 검증"""
    required_vars = ['GNEWS_API_KEY', 'OPENROUTER_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("=" * 70)
        print("⚠️  MISSING ENVIRONMENT VARIABLES")
        print("=" * 70)
        print("The following required variables are not set:")
        for var in missing_vars:
            print(f"  ✗ {var}")
        print()
        print("Please create a .env file in the project root with:")
        print("  GNEWS_API_KEY=your_gnews_api_key_here")
        print("  OPENROUTER_API_KEY=your_openrouter_api_key_here")
        print("=" * 70)
        return False
    
    print("✓ Environment variables validated")
    return True


def run_etl_pipeline(max_articles: int = 3):
    """
    ETL 파이프라인 실행
    
    Args:
        max_articles (int): 수집할 최대 기사 수
        
    Returns:
        dict: {
            'processed': int,
            'skipped': int,
            'errors': int
        }
    """
    print("=" * 70)
    print("TechExplained ETL Pipeline")
    print("=" * 70)
    print()
    
    # 환경 변수 검증
    if not check_environment():
        return {'processed': 0, 'skipped': 0, 'errors': 0}
    
    print()
    
    # ETL 컴포넌트 초기화
    fetcher = GNewsFetcher()
    scraper = WebScraper()
    analyzer = AIAnalyzer()
    loader = DBLoader(current_app.app_context())
    
    # Step 1: 기사 URL 수집
    print("STEP 1: Fetching articles from GNews API...")
    print("-" * 70)
    
    try:
        articles = fetcher.fetch_articles(max_results=max_articles)
    except Exception as e:
        print(f"\n✗ Failed to fetch articles: {e}")
        return {'processed': 0, 'skipped': 0, 'errors': 1}
    
    if not articles:
        print("\n✗ No articles fetched. Exiting.")
        return {'processed': 0, 'skipped': 0, 'errors': 0}
    
    print()
    
    # Step 2: 각 기사 처리
    print("STEP 2: Processing articles...")
    print("-" * 70)
    
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    for idx, article_data in enumerate(articles, 1):
        print(f"\n[Article {idx}/{len(articles)}]")
        print(f"Title: {article_data['title']}")
        print(f"URL: {article_data['url']}")
        
        try:
            # Step 2-1: 웹 스크래핑
            content = scraper.scrape_article(article_data['url'])
            
            if not content:
                print("  ✗ Failed to scrape content. Skipping.")
                error_count += 1
                continue
            
            # Step 2-2: AI 분석
            analysis = analyzer.analyze_article(content)
            
            if not analysis:
                print("  ✗ Failed to analyze content. Skipping.")
                error_count += 1
                continue
            
            # Step 2-3: 데이터베이스 적재
            print("  ⟳ Saving to database...")
            
            result = loader.load_article_data(
                article_data=article_data,
                analysis=analysis
            )
            
            if result:
                processed_count += 1
            else:
                skipped_count += 1
        
        except Exception as e:
            print(f"  ✗✗ Error processing article: {e}")
            error_count += 1
            continue
    
    # 최종 요약
    print()
    print("=" * 70)
    print("ETL Process Complete")
    print("=" * 70)
    print(f"✓ Successfully processed: {processed_count} articles")
    print(f"⊘ Skipped (already exists): {skipped_count} articles")
    print(f"✗ Errors: {error_count} articles")
    print(f"Total fetched: {len(articles)} articles")
    print("=" * 70)
    
    return {
        'processed': processed_count,
        'skipped': skipped_count,
        'errors': error_count
    }


if __name__ == "__main__":
    load_dotenv()
    
    print("[App Context] Flask 앱 컨텍스트를 생성합니다...")
    config_name = os.getenv('FLASK_ENV', 'development')
    app = create_app(config_name)
    
    with app.app_context():
        print("[App Context] Flask 앱 컨텍스트 생성 완료. ETL을 시작합니다.")
        run_etl_pipeline(max_articles=3)
        print("[App Context] ETL 작업 완료. DB 커밋이 보장됩니다.")

