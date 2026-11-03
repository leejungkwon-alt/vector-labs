# app/ops/env.py
"""
실행 환경 판정 (fail-closed).

SAJU_ENV 가 development / dev / local / test / testing 중 하나로 "명시"되어 있을 때만
개발 모드다. 미설정, 빈 문자열, 오타, staging 등 그 외 모든 값은 production 으로 취급한다.
(이전에는 SAJU_ENV == "production" 일 때만 보호가 켜져서, 환경변수가 빠지면
 mock 영수증/토큰과 개발용 JWT 기본 키가 열렸다.)
"""
import logging
import os

_NON_PROD_ENVS = frozenset({"development", "dev", "local", "test", "testing"})


def current_env() -> str:
    return os.environ.get("SAJU_ENV", "").strip().lower()


def is_production() -> bool:
    """명시적으로 개발 계열이 아니면 모두 production."""
    return current_env() not in _NON_PROD_ENVS


def validate_startup() -> None:
    """
    프로세스 시작 시 1회 호출. production 으로 판정되면 필수 설정을 즉시 검사한다.
    (Cloud Run 에서는 시작 실패 revision 이 트래픽을 받지 않아 이전 revision 이 유지된다.)
    """
    log = logging.getLogger("saju.security")
    if not is_production():
        log.warning(
            "SAJU_ENV=%r: non-production mode "
            "(mock tokens/receipts and the dev JWT secret are allowed).",
            current_env(),
        )
        return
    if not current_env():
        log.warning("SAJU_ENV is not set; treating as production (fail-closed).")
    from app.auth.jwt_utils import _secret

    _secret()  # 시크릿 누락 / 32자 미만이면 여기서 RuntimeError
