#!/usr/bin/env python3
"""
60일주 → 친근한 이름 매핑 적용.

1) 이미 작성된 13개 일주 파일에 `name` 필드 추가 (sinsal 형식)
2) `pillar_names.json` 생성 (ko/en, 60개 전체)
3) year/monthly/timeline 이 pillar_name 을 반환하도록 content_writer.py 패치

사용:
    python scripts/apply_pillar_names.py
    python scripts/apply_pillar_names.py --force
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "app" / "services" / "content" / "data"
CW = ROOT / "app" / "services" / "content_writer.py"


def _ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _backup(path: Path) -> Path:
    bak = path.with_suffix(path.suffix + f".bak.{_ts()}")
    shutil.copy2(path, bak)
    return bak


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


# ─────────────────────────────────────────────────────
# 13개 완성 일주에 붙일 semantic name
# ─────────────────────────────────────────────────────
SEMANTIC_NAMES = {
    "ko": {
        "丙申": "바위 위의 태양",
        "庚午": "제련로의 검",
        "丙子": "호수 위의 등불",
        "丙寅": "숲의 불꽃",
        "丙辰": "안개 낀 들판의 햇살",
        "丙午": "정오의 태양",
        "丙戌": "언덕 위의 화톳불",
        "丁丑": "비옥한 흙의 촛불",
        "丁卯": "봄나무 위의 촛불",
        "丁巳": "두 겹의 불꽃",
        "丁未": "메마른 땅의 촛불",
        "丁酉": "금속 위의 촛불",
        "丁亥": "수면 위의 촛불",
    },
    "en": {
        "丙申": "Sun Above Stone",
        "庚午": "Blade in the Forge",
        "丙子": "Lantern on a Lake",
        "丙寅": "Flame in the Forest",
        "丙辰": "Sunlight Over a Marsh",
        "丙午": "Noon Sun",
        "丙戌": "Hilltop Campfire",
        "丁丑": "Candle on Fertile Soil",
        "丁卯": "Candle on a Spring Branch",
        "丁巳": "Double Flame",
        "丁未": "Candle on Dry Earth",
        "丁酉": "Candle on Metal",
        "丁亥": "Candle on Water",
    },
}

# 한자 → 한글 독음 (traditional 필드 포맷: "병신(丙申)")
HANJA_TO_HANGUL = {
    "甲": "갑", "乙": "을", "丙": "병", "丁": "정", "戊": "무",
    "己": "기", "庚": "경", "辛": "신", "壬": "임", "癸": "계",
    "子": "자", "丑": "축", "寅": "인", "卯": "묘", "辰": "진", "巳": "사",
    "午": "오", "未": "미", "申": "신", "酉": "유", "戌": "술", "亥": "해",
}
STEMS = "甲乙丙丁戊己庚辛壬癸"
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"


def _all_60_pillars() -> list[str]:
    return [f"{STEMS[i % 10]}{BRANCHES[i % 12]}" for i in range(60)]


def _reading(pillar: str) -> str:
    return "".join(HANJA_TO_HANGUL.get(c, c) for c in pillar)


# ─────────────────────────────────────────────────────
# STEP 1: 기존 13개 일주 파일에 name / name_traditional 추가
# ─────────────────────────────────────────────────────
def step_pillar_files(force: bool = False) -> None:
    print("\n=== [1/3] 13개 일주 파일에 name 필드 추가 ===")
    created = skipped = 0

    for lang in ("ko", "en"):
        for pillar, name in SEMANTIC_NAMES[lang].items():
            path = DATA / lang / "core_pillars" / f"{pillar}.json"
            if not path.exists():
                print(f"  ❌ [{lang}] {pillar}.json 없음 (건너뜀)")
                continue

            data = _read_json(path)

            if data.get("name") and not force:
                print(f"  ⏭️  [{lang}] {pillar} 이미 name 있음")
                skipped += 1
                continue

            _backup(path)
            # sinsal 형식: name(친근) + name_traditional(한자)
            data["name"] = name
            data["name_traditional"] = f"{_reading(pillar)}({pillar})"
            _write_json(path, data)
            print(f"  ✅ [{lang}] {pillar} → \"{name}\"")
            created += 1

    print(f"  완료: {created}개 수정 / {skipped}개 건너뜀")


# ─────────────────────────────────────────────────────
# STEP 2: pillar_names.json (60개 전체, ko/en)
# ─────────────────────────────────────────────────────
def step_pillar_names_map(force: bool = False) -> None:
    print("\n=== [2/3] pillar_names.json 생성 (60개) ===")
    for lang in ("ko", "en"):
        path = DATA / lang / "pillar_names.json"
        if path.exists() and not force:
            print(f"  ⏭️  [{lang}] 이미 존재 (건너뜀, --force로 덮어쓰기)")
            continue
        if path.exists():
            _backup(path)

        mapping = {}
        for pillar in _all_60_pillars():
            if pillar in SEMANTIC_NAMES[lang]:
                mapping[pillar] = {
                    "name": SEMANTIC_NAMES[lang][pillar],
                    "traditional": f"{_reading(pillar)}({pillar})",
                }
            else:
                # 아직 파일 없는 일주는 reading을 name으로 fallback
                mapping[pillar] = {
                    "name": _reading(pillar),
                    "traditional": f"{_reading(pillar)}({pillar})",
                }

        _write_json(path, mapping)
        print(f"  ✅ [{lang}] pillar_names.json ({len(mapping)}개)")


# ─────────────────────────────────────────────────────
# STEP 3: content_writer.py 패치 (pillar_name 필드 추가)
# ─────────────────────────────────────────────────────
HELPER_SRC = '''

# ============================================================
# PILLAR NAME HELPER (Hanzi → 친근한 이름)
# ============================================================
def _get_pillar_display(pillar: str, lang: str) -> dict:
    """{'name': ..., 'traditional': ...} 반환. 없으면 빈 dict."""
    if not isinstance(pillar, str) or len(pillar) != 2:
        return {"name": "", "traditional": ""}
    try:
        names = load_pack(lang, "pillar_names")
    except KeyError:
        return {"name": pillar, "traditional": pillar}
    entry = names.get(pillar) or {}
    return {
        "name": entry.get("name", pillar),
        "traditional": entry.get("traditional", pillar),
    }
'''


def step_patch_writer(force: bool = False) -> None:
    print("\n=== [3/3] content_writer.py 패치 ===")
    if not CW.exists():
        print("  ❌ content_writer.py 없음")
        return

    src = CW.read_text(encoding="utf-8")

    if "_get_pillar_display" in src and not force:
        print("  ⏭️  이미 패치됨 (건너뜀, --force로 재적용)")
        return

    _backup(CW)

    # (a) helper 함수 추가 — 파일 끝에 append
    if "_get_pillar_display" not in src:
        src = src.rstrip() + "\n" + HELPER_SRC + "\n"

    # (b) write_core_section: "pillar": day_pillar, → + pillar_name 두 줄 추가
    src = re.sub(
        r'("pillar":\s*day_pillar,)',
        r'\1\n        "pillar_name": _get_pillar_display(day_pillar, lang)["name"],'
        r'\n        "pillar_name_traditional": _get_pillar_display(day_pillar, lang)["traditional"],',
        src,
        count=1,
    )

    # (c) write_year_section: "pillar": year_theme.get("pillar"),
    src = re.sub(
        r'("pillar":\s*year_theme\.get\("pillar"\),)',
        r'\1\n        **_get_pillar_display(year_theme.get("pillar"), lang),'
        r'\n        "pillar_name": _get_pillar_display(year_theme.get("pillar"), lang)["name"],',
        src,
        count=1,
    )

    # (d) write_monthly_section: items.append({...}) 안에 pillar_name 추가
    src = re.sub(
        r'("pillar":\s*m\["pillar"\],)',
        r'\1\n            "pillar_name": _get_pillar_display(m["pillar"], lang)["name"],'
        r'\n            "pillar_name_traditional": _get_pillar_display(m["pillar"], lang)["traditional"],',
        src,
        count=1,
    )

    # (e) write_timeline_section: items.append({...}) 안에 pillar_name 추가
    src = re.sub(
        r'("pillar":\s*d\["pillar"\],)',
        r'\1\n            "pillar_name": _get_pillar_display(d["pillar"], lang)["name"],'
        r'\n            "pillar_name_traditional": _get_pillar_display(d["pillar"], lang)["traditional"],',
        src,
        count=1,
    )

    CW.write_text(src, encoding="utf-8")
    print(f"  ✅ content_writer.py 패치 완료 (백업: {CW.name}.bak.*)")


# ─────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(description="60일주 친근한 이름 매핑 적용")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    step_pillar_files(force=args.force)
    step_pillar_names_map(force=args.force)
    step_patch_writer(force=args.force)

    print("\n✅ 완료. 다음으로 검증:")
    print("  pytest -q")
    print("\n서버 재시작 필수 (캐시 무효화).")
    print("\n⚠️  프론트엔드 업데이트 필요:")
    print("  - YearSection / MonthlySection / TimelineSection → section.pillar_name 사용")
    print("  - CoreSection → pillar_name 표시 (선택)")
    return 0


if __name__ == "__main__":
    sys.exit(main())