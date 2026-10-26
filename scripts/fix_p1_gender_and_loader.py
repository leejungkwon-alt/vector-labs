#!/usr/bin/env python3
"""
Step 2 (P1): 엔진 gender 화이트리스트 + loader list_available 중복 제거.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def patch(path_rel: str, old: str, new: str, label: str) -> bool:
    p = ROOT / path_rel
    if not p.exists():
        print(f"  ❌ {path_rel} 없음")
        return False
    src = p.read_text(encoding="utf-8")
    if old not in src:
        if new.split("\n")[0].strip() in src:
            print(f"  ⏭  {label} (already)")
            return True
        print(f"  ❌ {label}: 패턴 미발견")
        print(f"     {old[:100]!r}")
        return False
    (p.parent / (p.name + ".bak.p1")).write_text(src, encoding="utf-8")
    p.write_text(src.replace(old, new, 1), encoding="utf-8")
    print(f"  ✅ {label}")
    return True


def main() -> int:
    print("=" * 60)
    print("[Step 2] P1: gender 화이트리스트 + list_available 중복 제거")
    print("=" * 60)
    ok = True

    # ── 1. app/engine/daewoon.py — gender 화이트리스트 ──
    print("\n[1/2] app/engine/daewoon.py")
    ok &= patch(
        "app/engine/daewoon.py",
        (
            'def calculate_daewoon(utc_instant, gender, year_stem, solar_year, month_branch_idx):\n'
            '    utc_instant = _normalize_utc(utc_instant)\n'
            '\n'
            '    prev_term, next_term = get_adjacent_terms(utc_instant)\n'
            '\n'
            '    is_year_yang = year_stem in YANG_STEMS\n'
            '    is_male = gender.upper() in ("M", "남", "男性", "MALE")\n'
            '    is_forward = (is_year_yang and is_male) or (not is_year_yang and not is_male)\n'
        ),
        (
            'def calculate_daewoon(utc_instant, gender, year_stem, solar_year, month_branch_idx):\n'
            '    utc_instant = _normalize_utc(utc_instant)\n'
            '\n'
            '    # 화이트리스트: 스키마를 우회하는 호출(스크립트, telegram, 시각화)에서\n'
            '    # 빈 문자열이나 알 수 없는 값이 조용히 여성(역행)으로 처리되는 것을 방지한다.\n'
            '    g = (gender or "").strip().upper()\n'
            '    _MALE_TOKENS = ("M", "남", "男性", "MALE")\n'
            '    _FEMALE_TOKENS = ("F", "여", "女性", "FEMALE")\n'
            '    if g in _MALE_TOKENS:\n'
            '        is_male = True\n'
            '    elif g in _FEMALE_TOKENS:\n'
            '        is_male = False\n'
            '    else:\n'
            '        raise ValueError(\n'
            '            f"gender must be one of {_MALE_TOKENS + _FEMALE_TOKENS} "\n'
            '            f"(got {gender!r})."\n'
            '        )\n'
            '\n'
            '    prev_term, next_term = get_adjacent_terms(utc_instant)\n'
            '\n'
            '    is_year_yang = year_stem in YANG_STEMS\n'
            '    is_forward = (is_year_yang and is_male) or (not is_year_yang and not is_male)\n'
        ),
        "gender 화이트리스트",
    )

    # ── 2. app/services/content/loader.py — 중복 list_available 제거 ──
    print("\n[2/2] app/services/content/loader.py")
    p = ROOT / "app/services/content/loader.py"
    src = p.read_text(encoding="utf-8")
    # 뒤쪽 중복 정의를 찾아 삭제 (마커 기반)
    dup_pattern = re.compile(
        r'\n\ndef list_available\(lang: str\) -> list:\n'
        r'    """해당 언어에서 사용 가능한 섹션 목록\."""\n'
        r'    return list\(_REGISTRY\.get\(lang, \{\}\)\.keys\(\)\)\n?'
    )
    matches = dup_pattern.findall(src)
    if not matches:
        if src.count("def list_available") == 1:
            print("  ⏭  이미 정리됨 (1회만 정의)")
        else:
            print(f"  ❌ 패턴 미발견 — 수동 확인 필요 (def 개수: {src.count('def list_available')})")
            ok = False
    else:
        (p.parent / (p.name + ".bak.p1")).write_text(src, encoding="utf-8")
        new_src = dup_pattern.sub("\n", src, count=1)
        p.write_text(new_src, encoding="utf-8")
        print(f"  ✅ 중복 list_available {len(matches)}개 제거")

    # ── 3. 테스트 추가 ──
    print("\n[test] tests/test_p1_regressions.py (신규)")
    test_file = ROOT / "tests/test_p1_regressions.py"
    if test_file.exists():
        print("  ⏭  이미 존재")
    else:
        test_file.write_text(
            '''"""P1 회귀: daewoon gender 화이트리스트 + loader 중복 정의."""
import pytest
from datetime import datetime, timezone

from app.engine.daewoon import calculate_daewoon
from app.services.content.loader import list_available


_KST = timezone.utc


# ── gender 화이트리스트 ──
def _calc(gender):
    return calculate_daewoon(
        utc_instant=datetime(1990, 5, 5, 5, 30, tzinfo=_KST),
        gender=gender,
        year_stem="庚",
        solar_year=1990,
        month_branch_idx=4,
    )


@pytest.mark.parametrize("g", ["M", "m", "남", "MALE", " male ", "남성X"])
def test_male_tokens_forward(g):
    # '남성X'는 화이트리스트 밖 → ValueError 여야 함
    if g.strip().upper() not in ("M", "남", "MALE"):
        with pytest.raises(ValueError):
            _calc(g)
    else:
        assert _calc(g)["is_forward"] is True


@pytest.mark.parametrize("g", ["F", "f", "여", "FEMALE", " female "])
def test_female_tokens_backward(g):
    assert _calc(g)["is_forward"] is False


@pytest.mark.parametrize("g", ["", "X", "other", None, "  "])
def test_invalid_gender_raises(g):
    with pytest.raises(ValueError, match="gender must be one of"):
        _calc(g)


# ── list_available ──
def test_list_available_returns_json_based_lists():
    """JSON 디렉터리 기반 함수가 살아있어야 함 (en JSON 파일들 인식)."""
    sections = list_available("en")
    # JSON 팩에 존재하는 섹션
    for expected in ("core", "compatibility", "daily", "sections"):
        assert expected in sections, f"{expected} not in {sections}"


def test_list_available_unknown_lang_empty():
    """미지원 언어는 빈 리스트 (크래시 없음)."""
    assert list_available("xx") == []


def test_list_available_ja_or_zh_if_present():
    """ja/zh_cn JSON 이 있으면 자동 인식, 없으면 빈 리스트."""
    import pathlib
    data_root = pathlib.Path("app/services/content/data")
    for lang in ("ja", "zh_cn", "zh_tw"):
        if (data_root / lang).exists() and any((data_root / lang).glob("*.json")):
            assert list_available(lang), f"{lang} JSON 있는데 빈 리스트"
''',
            encoding="utf-8",
        )
        print("  ✅ 생성")

    print("\n" + "=" * 60)
    print("✅ 완료" if ok else "❌ 일부 실패")
    print("=" * 60)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())