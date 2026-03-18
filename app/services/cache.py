"""
[app/services/cache.py]
Redis를 사용한 대화 내역(Context) 캐싱 및 임시 세션 관리를 담당하는 모듈입니다.
현재는 구조만 잡혀 있으며, 추후 Redis 서버 설정 시 구현됩니다.
"""

import logging

logger = logging.getLogger("cache_service")

class CacheService:
    def __init__(self):
        # TODO: Redis 클라이언트 초기화 (redis-py 설치 후)
        # self.redis_client = None
        pass

    @staticmethod
    def get_conversation_history(user_id: str):
        """
        특정 유저의 대화 내용을 Redis에서 가져옵니다.
        """
        logger.info(f"💾 [Cache] Fetching history for user {user_id}")
        return [] # 현재는 비어있는 리스트 반환

    @staticmethod
    def save_chat(user_id: str, message: str, role: str):
        """
        신규 대화를 Redis에 저장합니다.
        """
        logger.info(f"💾 [Cache] Saved {role} message for {user_id}")
        pass

cache_service = CacheService()
