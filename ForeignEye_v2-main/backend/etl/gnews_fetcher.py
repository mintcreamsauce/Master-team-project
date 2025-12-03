"""
GNews API 크롤러

GNews API를 통해 기술 뉴스를 수집합니다.
"""

import os
import requests
from typing import List, Dict, Optional


class GNewsFetcher:
    """GNews API 기사 수집 클래스"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key (str, optional): GNews API 키. None이면 환경 변수에서 로드
        """
        self.api_key = api_key or os.getenv('GNEWS_API_KEY')
        
        if not self.api_key:
            raise ValueError("GNEWS_API_KEY not found. Please set it in .env file.")
        
        self.base_url = "https://gnews.io/api/v4/top-headlines"
    
    def fetch_articles(
        self,
        category: str = 'technology',
        lang: str = 'en',
        country: str = 'us',
        max_results: int = 3
    ) -> List[Dict[str, str]]:
        """
        GNews API에서 기사 목록 가져오기
        
        Args:
            category (str): 카테고리 (기본값: 'technology')
            lang (str): 언어 (기본값: 'en')
            country (str): 국가 (기본값: 'us')
            max_results (int): 최대 결과 수 (기본값: 3)
            
        Returns:
            List[Dict]: [{'title': str, 'url': str}, ...]
            
        Raises:
            requests.exceptions.RequestException: API 요청 실패 시
        """
        params = {
            'category': category,
            'lang': lang,
            'country': country,
            'max': max_results,
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article in data.get('articles', []):
                articles.append({
                    'title': article.get('title', 'No title'),
                    'url': article.get('url', ''),
                    'description': article.get('description', ''),
                    'published_at': article.get('publishedAt', ''),
                    'source': article.get('source', {}).get('name', 'Unknown')
                })
            
            print(f"✓ Successfully fetched {len(articles)} articles from GNews API")
            return articles
        
        except requests.exceptions.Timeout:
            print(f"✗ Timeout error: GNews API took too long to respond")
            raise
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print(f"✗ Authentication error: Invalid API key")
            elif e.response.status_code == 429:
                print(f"✗ Rate limit exceeded: Too many requests")
            else:
                print(f"✗ HTTP error: {e}")
            raise
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching from GNews API: {e}")
            raise
    
    def validate_api_key(self) -> bool:
        """
        API 키 유효성 검증
        
        Returns:
            bool: 유효하면 True
        """
        try:
            params = {
                'category': 'technology',
                'lang': 'en',
                'country': 'us',
                'max': 1,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=5)
            return response.status_code == 200
        
        except Exception:
            return False

