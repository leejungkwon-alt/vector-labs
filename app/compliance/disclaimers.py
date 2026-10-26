"""
표준 disclaimer + 금지 표현 검출.

리포트의 DISCLAIMER 는 각 언어팩(data/{lang}/sections.json)이 유일 소스다.
이 모듈은 그 팩에서 값을 읽어 앱·PDF·마케팅 등 다른 표면에서 재사용 가능하게
노출한다. 하드코딩된 문구를 여기 두지 않는 이유는 이중 정의로 인한 불일치
(과거: compliance 와 sections.json 이 서로 다른 문구였음) 를 원천 차단하기 위함.
"""
from app.services.content.loader import load_pack


# 팩 로드 실패(파일 없음/언어 미지원) 시 사용할 최소 fallback.
# 실제 운영에서는 항상 sections.json 이 우선된다.
_EN_FALLBACK = (
    "Note: This report combines astronomical calculations with modern coaching "
    "frameworks for personal insight and entertainment. It is not medical, financial, "
    "or psychological advice. Traditional Four Pillars analysis is school-dependent. "
    "If you are in crisis, contact local emergency services or a suicide prevention "
    "hotline. If you are outside the US, see https://findahelpline.com/."
)

_KO_FALLBACK = (
    "안내: 본 리포트는 천문 계산과 현대 심리 코칭을 결합하여 자기 이해와 오락을 "
    "목적으로 제공됩니다. 의료·금융·심리 상담이 아닙니다. 사주 해석은 유파에 따라 "
    "달라질 수 있습니다. 위기 상황이라면 지역 응급 서비스나 자살예방 핫라인에 "
    "연락하세요. 지역별 핫라인은 https://findahelpline.com/ 에서 확인할 수 있습니다."
)


def _load_disclaimer(lang: str, fallback: str) -> str:
    """data/{lang}/sections.json 의 DISCLAIMER 를 우선 사용. 실패 시 fallback."""
    try:
        value = load_pack(lang, "sections").get("DISCLAIMER")
        if value:
            return value
    except Exception:
        pass
    return fallback


# 모듈 로드 시점에 팩을 읽어 상수에 바인딩.
# content.loader 는 lru-style 캐시를 쓰므로 추가 I/O 부담 없음.
DISCLAIMER_KO = _load_disclaimer("ko", _KO_FALLBACK)
DISCLAIMER_EN = _load_disclaimer("en", _EN_FALLBACK)


# 금지 표현: 미래 단정, 100% 확신, 운명 결정론
FORBIDDEN_PHRASES = (
    "your destiny is",
    "당신의 운명은",
    "guaranteed to",
    "100% accurate",
    "100% 정확",
    "definitely will",
    "반드시 일어날",
    "you will certainly",
)


def get_disclaimer(lang: str) -> str:
    if lang == "ko":
        return DISCLAIMER_KO
    return DISCLAIMER_EN


def contains_forbidden_claims(text: str) -> list:
    """금지 표현 목록 반환. 빈 리스트 = 통과."""
    if not text:
        return []
    t = text.lower()
    return [p for p in FORBIDDEN_PHRASES if p.lower() in t]