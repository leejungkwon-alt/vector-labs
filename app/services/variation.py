"""
Seed 기반 결정론적 변형 선택 엔진 (Step 3).

목적: 동일한 semantic 결과가 유저/날짜/스코프별로 자연스럽게 다른 표현을 갖도록.

원칙:
  - 프로세스 간 결정론 (sha256 사용, Python hash() 사용 금지)
  - user_id > birth_date > "anonymous" 우선순위
  - 변형 리스트가 비어있으면 예외
"""
from __future__ import annotations

import hashlib
from typing import Any, Sequence


def _stable_hash(*parts: Any) -> int:
    """프로세스 간 안정적인 해시 (Python hash()는 seed 랜덤)."""
    payload = "|".join(str(p) for p in parts if p is not None)
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def pick_variant(
    variants: Sequence[Any],
    *,
    seed_parts: Sequence[Any],
) -> Any:
    """
    seed_parts로부터 결정론적으로 variants 중 하나를 반환.

    - 같은 seed_parts → 같은 결과 (프로세스 간에도 동일)
    - variants 비어있으면 ValueError
    """
    if not variants:
        raise ValueError("variants must not be empty")
    idx = _stable_hash(*seed_parts) % len(variants)
    return variants[idx]


def make_seed(
    *,
    user_id: str | None,
    birth_date: str | None,
    scope: str,
    discriminator: str,
) -> tuple:
    """
    표준 시드 튜플 생성.

    Args:
        user_id: 인증된 유저 ID (없으면 None)
        birth_date: YYYY-MM-DD (없으면 None)
        scope: "daily" / "monthly" / "year" 등 콘텐츠 스코프
        discriminator: 날짜, 월 인덱스, 테마 키 등 스코프 내 구분자
    """
    anchor = user_id or birth_date or "anonymous"
    return (anchor, scope, discriminator)
