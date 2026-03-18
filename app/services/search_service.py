"""
[app/services/search_service.py]
Tavily 검색 엔진을 통해 외부 정보를 조회하는 기능을 담당합니다.
Tavily는 AI 에이전트에 최적화된 검색 결과(JSON, Summary 등)를 제공합니다.
"""

import os
import logging
from tavily import TavilyClient

logger = logging.getLogger("search_service")

class SearchService:
    def __init__(self):
        # 환경 변수에서 TAVILY_API_KEY를 가져옵니다.
        # 키가 없을 경우를 대비해 초기화는 하되, 실행 시점에서 체크합니다.
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.client = None
        if self.api_key:
            self.client = TavilyClient(api_key=self.api_key)
            logger.info("✅ TavilyClient 초기화 완료.")
        else:
            logger.warning("⚠️ TAVILY_API_KEY가 설정되지 않았습니다. 외부 검색이 작동하지 않을 수 있습니다.")

    async def search_web(self, query: str) -> str:
        """
        Tavily API를 사용하여 웹 검색을 수행합니다.
        """
        # 실행 시점에 환경 변수를 다시 한 번 확인합니다.
        if not self.client:
            self.api_key = os.getenv("TAVILY_API_KEY")
            if self.api_key and not self.api_key.startswith("tvly-your"):
                self.client = TavilyClient(api_key=self.api_key)
                logger.info("✅ TavilyClient가 런타임에 성공적으로 초기화되었습니다.")
            else:
                logger.error("❌ TAVILY_API_KEY가 유효하지 않거나 설정되지 않았습니다.")
                return "기능 오류: 서비스의 API 키 설정이 올바르지 않습니다."

        logger.info(f"🌐 Tavily 외부 웹 검색 수행 중: {query}")
        try:
            response = self.client.search(query=query, search_depth="basic")
            results = response.get('results', [])
            
            if not results:
                logger.warning(f"⚠️ '{query}'에 대한 검색 결과가 없습니다.")
                return "관련된 최신 웹 검색 결과가 없습니다."
                
            formatted_results = []
            for res in results[:3]:
                formatted_results.append(f"제목: {res['title']}\n내용: {res['content']}\nURL: {res['url']}")
            
            logger.info(f"✅ {len(results)}개의 검색 결과를 찾았습니다.")
            return "\n\n".join(formatted_results)
            
        except Exception as e:
            logger.error(f"❌ Tavily API 연동 에러: {e}")
            return f"웹 검색 수행 중 오류가 발생했습니다: {str(e)}"

# 싱글톤으로 인스턴스 제공
search_service = SearchService()
