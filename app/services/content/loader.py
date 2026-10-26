# app/services/content/loader.py
"""
콘텐츠 팩 로더.

언어별, 섹션별 팩을 가져온다.
지금은 Python 모듈. 나중에 JSON/YAML로 바꿔도 인터페이스는 유지.
"""

# 언어별 팩 레지스트리. 새 언어 추가 시 여기만 갱신.
import json

_CACHE: dict = {}

# 언어팩이 아직 없는 신규 언어(es 등)를 en으로 폴백할 때 허용할 목록.
# 여기 없는 값(xx, fr 등)은 KeyError로 fail-fast해서, 알 수 없는 lang이
# 조용히 en 콘텐츠를 받는 것을 막는다.
_SUPPORTED_FALLBACK_LANGS = frozenset({"en", "ko", "ja", "zh_cn", "es"})

def load_pack(lang: str, section: str) -> dict:
    """
    언어·섹션 팩을 로드.

    JSON 파일 우선 로드 (data/{lang}/{section}.json).
    파일이 없으면 KeyError.
    """
    cache_key = (lang, section)
    if cache_key in _CACHE:
        return _CACHE[cache_key]

    import pathlib
    data_path = pathlib.Path(__file__).parent / "data" / lang / f"{section}.json"

    if data_path.exists():
        with open(data_path, "r", encoding="utf-8") as f:
            pack = json.load(f)
        _CACHE[cache_key] = pack
        return pack

    # 신규 언어(es 등)의 data/{lang}/ 팩이 아직 없으면 en으로 폴백.
    # 화이트리스트(_SUPPORTED_FALLBACK_LANGS)에 있는 언어만 — 알 수 없는
    # 화이트리스트 밖의 lang은 아래에서 KeyError로 fail-fast.
    if lang in _SUPPORTED_FALLBACK_LANGS and lang != "en":
        en_path = pathlib.Path(__file__).parent / "data" / "en" / f"{section}.json"
        if en_path.exists():
            with open(en_path, "r", encoding="utf-8") as f:
                pack = json.load(f)
            _CACHE[cache_key] = pack
            return pack

    raise KeyError(f"Data file not found: {data_path}")


def load_labels(lang: str) -> dict:
    """UI 라벨 팩. ko/en만 존재하므로 미지원 언어는 en으로 폴백."""
    try:
        return load_pack(lang, "labels")
    except KeyError:
        return load_pack("en", "labels")


def load_errors(lang: str) -> dict:
    """에러 메시지 팩. ko/en만 존재하므로 미지원 언어는 en으로 폴백."""
    try:
        return load_pack(lang, "errors")
    except KeyError:
        return load_pack("en", "errors")


def list_available(lang: str) -> list:
    """해당 언어에서 사용 가능한 섹션 목록 (JSON 파일 기준)."""
    import pathlib
    lang_dir = pathlib.Path(__file__).parent / "data" / lang
    if lang_dir.exists():
        return sorted(p.stem for p in lang_dir.glob("*.json"))
    return []

