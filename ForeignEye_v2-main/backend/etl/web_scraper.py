"""
웹 스크래퍼

주어진 URL에서 기사 본문을 추출합니다.
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional


class WebScraper:
    """웹 페이지 스크래핑 클래스"""
    
    def __init__(self, timeout: int = 15):
        """
        Args:
            timeout (int): 요청 타임아웃 (초)
        """
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_article(self, url: str) -> Optional[str]:
        """
        URL에서 기사 본문 추출
        
        Args:
            url (str): 기사 URL
            
        Returns:
            str: 추출된 텍스트. 실패 시 None
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 본문 추출 (여러 전략 시도)
            article_text = self._extract_text(soup)
            
            if not article_text:
                print(f"  ✗ No content found in article: {url}")
                return None
            
            print(f"  ✓ Scraped {len(article_text)} characters from {url}")
            return article_text
        
        except requests.exceptions.Timeout:
            print(f"  ✗ Timeout error while scraping: {url}")
            return None
        
        except requests.exceptions.HTTPError as e:
            print(f"  ✗ HTTP error {e.response.status_code}: {url}")
            return None
        
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Request error while scraping: {e}")
            return None
        
        except Exception as e:
            print(f"  ✗ Unexpected error while scraping: {e}")
            return None
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """
        BeautifulSoup 객체에서 텍스트 추출
        
        전략:
        1. <article> 태그 찾기
        2. <p> 태그들 수집
        3. 스크립트, 스타일 제거
        
        Args:
            soup (BeautifulSoup): 파싱된 HTML
            
        Returns:
            str: 추출된 텍스트
        """
        # 불필요한 태그 제거
        for script in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            script.decompose()
        
        # 전략 1: <article> 태그 찾기
        article_tag = soup.find('article')
        if article_tag:
            paragraphs = article_tag.find_all('p')
            if paragraphs:
                text = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                if len(text) > 200:  # 최소 길이 확인
                    return text
        
        # 전략 2: 모든 <p> 태그 수집
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        return text
    
    def scrape_multiple(self, urls: list) -> dict:
        """
        여러 URL을 한 번에 스크래핑
        
        Args:
            urls (list): URL 리스트
            
        Returns:
            dict: {url: content or None}
        """
        results = {}
        
        for url in urls:
            results[url] = self.scrape_article(url)
        
        return results

