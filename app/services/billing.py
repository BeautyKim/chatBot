"""
[app/services/billing.py]
사용자 크레딧 차감 및 결제 관련 로직을 담당하는 플레이스홀더 모듈입니다.
추후 스프링 백엔드나 결제 시스템 연동 시 구현 예정입니다.
"""

import logging

logger = logging.getLogger("billing_service")

class BillingService:
    @staticmethod
    def deduct_credit(user_id: str, cost: float):
        """
        사용자의 크레딧을 차감하는 로직이 들어갈 곳입니다.
        현재는 로그만 남기고 통과(Pass)시킵니다.
        """
        logger.info(f"💰 [Billing] User {user_id} credit used. Estimated cost: {cost}")
        # TODO: 크레딧 부족 시 에러 발생 시키는 로직 등 추가 예정
        pass

billing_service = BillingService()
