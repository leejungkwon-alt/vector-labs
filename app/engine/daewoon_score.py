# app/engine/daewoon_score.py
"""
인생의 큰 흐름 점수화.

각 인생의 큰 흐름의 하늘의 기운과 땅의 기운(본기) 오행이
나에게 힘이 되는 기운/나를 도와주는 기운이면 +, 조심해야 할 기운이면 - 로 점수를 매긴다.

가중치:
  하늘의 기운: 1.0
  땅의 기운: 2.0 (땅의 기운가 인생의 큰 흐름에서 더 강한 영향)

점수 범위: -3.0 (전부 조심해야 할 기운) ~ +3.0 (전부 나에게 힘이 되는 기운)
"""
from app.engine.elements import (
    STEM_TO_ELEMENT,
    BRANCH_MAIN_STEM,
)


def _element_score(elem: str, yongsin_info: dict) -> float:
    """오행 하나의 가점/감점."""
    if elem == yongsin_info["yongsin"]:
        return 1.0
    if elem == yongsin_info["huisin"]:
        return 0.5
    if elem in yongsin_info["gisin"]:
        return -1.0
    return 0.0


def _grade(score: float) -> str:
    """점수 → 등급 코드(언어 중립). 표시 라벨은 콘텐츠 계층에서."""
    if score >= 2.0:
        return "PEAK"
    if score >= 1.0:
        return "FAVORABLE"
    if score > -1.0:
        return "NEUTRAL"
    if score > -2.0:
        return "CAUTION"
    return "CHALLENGING"


def score_daewoon(daewoon_pillars: list, yongsin_info: dict) -> list:
    """
    인생의 큰 흐름 리스트에 점수와 등급을 부여.

    Args:
        daewoon_pillars: calculate_daewoon()의 결과에서 온 리스트.
                        각 항목: {"daewoon_index", "start_age", "end_age", "pillar"}
        yongsin_info: derive_useful_god()의 반환값.

    Returns:
        각 항목에 아래 필드가 추가된 리스트:
          score:      -3.0 ~ +3.0 (float)
          grade:      {"ko": ..., "en": ...}
          stem_elem:  하늘의 기운 오행
          branch_elem: 땅의 기운 본기 오행
          favorable:  이 인생의 큰 흐름이 우호적인가
    """
    scored = []

    for dw in daewoon_pillars:
        pillar = dw.get("pillar", "")
        if len(pillar) != 2:
            continue

        stem_elem = STEM_TO_ELEMENT.get(pillar[0], "")
        branch_main = BRANCH_MAIN_STEM.get(pillar[1], "")
        branch_elem = STEM_TO_ELEMENT.get(branch_main, "")

        stem_score = _element_score(stem_elem, yongsin_info) * 1.0
        branch_score = _element_score(branch_elem, yongsin_info) * 2.0
        total = round(stem_score + branch_score, 2)

        scored.append({
            **dw,
            "score": total,
            "grade": _grade(total),
            "stem_elem": stem_elem,
            "branch_elem": branch_elem,
            "favorable": total > 0,
        })

    return scored


def summarize_daewoon_timeline(scored: list) -> dict:
    """인생의 큰 흐름 점수 리스트를 요약. 최고/최저 인생의 큰 흐름, 전체 흐름."""
    if not scored:
        return {
            "best": None,
            "worst": None,
            "average_score": 0.0,
            "positive_count": 0,
            "negative_count": 0,
        }

    best = max(scored, key=lambda x: x["score"])
    worst = min(scored, key=lambda x: x["score"])
    avg = round(sum(x["score"] for x in scored) / len(scored), 2)

    return {
        "best": best,
        "worst": worst,
        "average_score": avg,
        "positive_count": sum(1 for x in scored if x["score"] > 0),
        "negative_count": sum(1 for x in scored if x["score"] < 0),
    }