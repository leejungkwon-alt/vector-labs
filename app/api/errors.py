"""
API 에러 메시지 로컬라이즈 헬퍼.

시간 보정 엔진의 구조화 예외(DSTAmbiguousError / DSTGapError)를
lang별 사용자 메시지로 포맷. 데이터는 data/{lang}/errors.json.
"""
from app.engine.time_correction import DSTAmbiguousError, DSTGapError
from app.services.content.loader import load_errors


_EN_FALLBACK = {
    "DST_AMBIGUOUS": (
        "This clock time is ambiguous: {clock} occurs twice in {tz}. "
        "Re-request with dst_fold=0 (offset {off0}) or "
        "dst_fold=1 (offset {off1})."
    ),
    "DST_GAP": (
        "This clock time does not exist: {clock} is skipped by DST in {tz}."
    ),
}


def format_dst_error(lang: str, exc: Exception) -> str:
    """DST 구조화 예외를 lang별 사용자 메시지로 변환. 실패 시 EN fallback."""
    if isinstance(exc, DSTAmbiguousError):
        key = "DST_AMBIGUOUS"
        fmt_vars = {
            "clock": exc.clock, "tz": exc.tz_key,
            "off0": exc.off0, "off1": exc.off1,
        }
    elif isinstance(exc, DSTGapError):
        key = "DST_GAP"
        fmt_vars = {"clock": exc.clock, "tz": exc.tz_key}
    else:
        return str(exc)

    try:
        tpl = load_errors(lang).get(key) or _EN_FALLBACK[key]
    except Exception:
        tpl = _EN_FALLBACK[key]

    try:
        return tpl.format(**fmt_vars)
    except (KeyError, ValueError, IndexError):
        return _EN_FALLBACK[key].format(**fmt_vars)
