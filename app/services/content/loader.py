# app/services/content/loader.py
"""
콘텐츠 팩 로더.

언어별, 섹션별 팩을 가져온다.
지금은 Python 모듈. 나중에 JSON/YAML로 바꿔도 인터페이스는 유지.
"""

# 언어별 팩 레지스트리. 새 언어 추가 시 여기만 갱신.
import json
_REGISTRY = {
    "en": {
        "core": "app.services.content.en.core",
        "sections": "app.services.content.en.sections",
        "energy": "app.services.content.en.energy",
        "lucky_code": "app.services.content.en.lucky_code",
        "year": "app.services.content.en.year",
        "health": "app.services.content.en.health",
        "age_band": "app.services.content.en.age_band",
        "monthly": "app.services.content.en.monthly", "sinsal": "app.services.content.en.sinsal",
        "compatibility": "app.services.content.en.compatibility",
        "personalization": "app.services.content.en.personalization",
        "daily": "app.services.content.en.daily",
    },
    "ko": {
        "core": "app.services.content.ko.core",
        "sections": "app.services.content.ko.sections",
        "energy": "app.services.content.ko.energy",
        "lucky_code": "app.services.content.ko.lucky_code",
        "year": "app.services.content.ko.year",
        "health": "app.services.content.ko.health",
        "age_band": "app.services.content.ko.age_band",
        "monthly": "app.services.content.ko.monthly", "sinsal": "app.services.content.ko.sinsal",
        "compatibility": "app.services.content.ko.compatibility",
        "personalization": "app.services.content.ko.personalization",
        "daily": "app.services.content.ko.daily",
    },
}

_CACHE: dict = {}


def load_pack(lang: str, section: str) -> dict:
    """
    언어·섹션 팩을 로드.

    JSON 파일 우선 로드 (data/{lang}/{section}.json).
    파일이 없으면 기존 _REGISTRY 기반 KeyError.
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

    if lang not in _REGISTRY:
        raise KeyError(f"Language pack not registered: {lang}")
    if section not in _REGISTRY[lang]:
        raise KeyError(f"Section '{section}' not available for lang '{lang}'")
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
    return list(_REGISTRY.get(lang, {}).keys())


def list_available(lang: str) -> list:
    """해당 언어에서 사용 가능한 섹션 목록."""
    return list(_REGISTRY.get(lang, {}).keys())
