#!/usr/bin/env python3
"""
P2: EN awkward phrases 수정 (10 instances / 6 unique strings).
- 안전: 정확한 문자열 치환 + 저장 전 JSON 파싱 검증 + .bak 백업
- 테스트 파일도 함께 갱신 (career.headline golden assert)
- 수정 후 잔존 패턴 스캔
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EN_DATA = ROOT / "app/services/content/data/en"

# === JSON 콘텐츠 수정 ===
REPLACEMENTS = {
    "career.json": [
        # 1. THE_RADIATOR.headline
        ("You shine on stage, such as in sales, marketing, and presentations.",
         "You shine on stage — in sales, marketing, and presentations."),
        # 2. THE_CULTIVATOR.headline
        ("Suited for growing people, such as in education, planning, and HR.",
         "Suited for growing people — in education, planning, and HR."),
    ],
    "love.json": [
        # 3 + 4. THE_PIONEER.body 내 두 문장
        ("You have no aversion to leading your partner and presenting the path forward.",
         "You are comfortable leading your partner and mapping out the way forward."),
        ("Your true strength is the power to open the way. When you use this power together with your partner, the relationship becomes richer.",
         "Your real gift is opening the way. When you share that gift with your partner, the relationship becomes richer."),
    ],
    "premium_insights.json": [
        # 5. favorable
        ("Currently, you are in a big life flow of {pillar} from age {start_age} to {end_age}. "
         "This period has a relatively strong energy pushing your grain. {section_angle}",
         "You are currently in a major life chapter ruled by {pillar}, from age {start_age} to {end_age}. "
         "This period carries a strong tailwind that amplifies your natural rhythm. {section_angle}"),
        # 6. neutral
        ("Currently, you are in a big life flow of {pillar} from age {start_age} to {end_age}. "
         "This period has both pushing and shaking energies, so the same situation can feel very "
         "different depending on your choices. {section_angle}",
         "You are currently in a major life chapter ruled by {pillar}, from age {start_age} to {end_age}. "
         "This period mixes tailwinds and headwinds, so the same situation can feel very different "
         "depending on your choices. {section_angle}"),
        # 7. caution
        ("Currently, you are in a big life flow of {pillar} from age {start_age} to {end_age}. "
         "This is a period where you need to take more careful care of yourself. {section_angle}",
         "You are currently in a major life chapter ruled by {pillar}, from age {start_age} to {end_age}. "
         "This is a period when you need to take especially careful care of yourself. {section_angle}"),
        # 8. no_daewoon
        ("The detailed flow of your big life flow is not yet sufficiently revealed, "
         "so I will read focusing on this year's flow and this month's energy.",
         "Your major life chapter is still taking shape, so this reading focuses on "
         "this year's momentum and this month's energy."),
    ],
    "year.json": [
        # 9. TEN_GOD_HURTING_OFFICER[1].body
        ("Throughout the year, confidently raising your voice to the world will give you the "
         "experience of standing tall as the protagonist of the stage. "
         "Enjoy the joy of your name becoming a powerful brand.",
         "Throughout the year, confidently raising your voice to the world will let you "
         "experience taking center stage. Enjoy watching your name become a powerful brand."),
    ],
}

# === 테스트 파일 갱신 ===
TEST_UPDATES = {
    "tests/test_premium_content.py": [
        ('        "You shine on stage, such as in sales, marketing, and presentations."',
         '        "You shine on stage — in sales, marketing, and presentations."'),
    ],
}

# === 잔존 검사 패턴 (수정 후 0건이어야 통과) ===
RESIDUAL_PATTERNS = {
    "career.json": ["such as in"],
    "love.json": ["no aversion to", "the power to open the way"],
    "premium_insights.json": ["big life flow", "pushing your grain"],
    "year.json": ["the protagonist of the stage"],
}


def apply_to_json(filepath: Path, pairs):
    text = filepath.read_text(encoding="utf-8")
    original = text
    applied, missed = [], []

    for old, new in pairs:
        if old in text:
            text = text.replace(old, new, 1)
            applied.append(old[:60].replace("\n", " ") + "…")
        else:
            missed.append(old[:60].replace("\n", " ") + "…")

    if text != original:
        try:
            json.loads(text)
        except json.JSONDecodeError as e:
            print(f"  ❌ {filepath.name}: JSON 파싱 실패 → 저장 취소 ({e})")
            return [], missed + ["(JSON invalid)"]
        (filepath.with_suffix(filepath.suffix + ".bak")).write_text(original, encoding="utf-8")
        filepath.write_text(text, encoding="utf-8")

    return applied, missed


def apply_to_text(filepath: Path, pairs):
    text = filepath.read_text(encoding="utf-8")
    original = text
    applied, missed = [], []

    for old, new in pairs:
        if old in text:
            text = text.replace(old, new, 1)
            applied.append(old[:60])
        else:
            missed.append(old[:60])

    if text != original:
        (filepath.with_suffix(filepath.suffix + ".bak")).write_text(original, encoding="utf-8")
        filepath.write_text(text, encoding="utf-8")

    return applied, missed


def verify_residual() -> int:
    print("\n[검증] 잔존 awkward 패턴 스캔")
    total = 0
    for fname, patterns in RESIDUAL_PATTERNS.items():
        path = EN_DATA / fname
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        remaining = [p for p in patterns if p in text]
        if remaining:
            total += len(remaining)
            print(f"  ❌ {fname}: {remaining}")
        else:
            print(f"  ✅ {fname}: 깨끗")
    return total


def main() -> int:
    print("[P2] EN awkward phrases 수정")
    print("=" * 60)

    total_applied = total_missed = 0

    for fname, pairs in REPLACEMENTS.items():
        fpath = EN_DATA / fname
        if not fpath.exists():
            print(f"\n⚠️  {fname} 없음 — 건너뜀")
            continue
        print(f"\n📄 {fname}")
        applied, missed = apply_to_json(fpath, pairs)
        for a in applied:
            print(f"  ✅ {a}")
        for m in missed:
            print(f"  ⚠️  미발견: {m}")
        total_applied += len(applied)
        total_missed += len(missed)

    # 테스트 파일 갱신
    print("\n[테스트 갱신]")
    for rel, pairs in TEST_UPDATES.items():
        fpath = ROOT / rel
        if not fpath.exists():
            print(f"  ⚠️  {rel} 없음")
            continue
        print(f"  📄 {rel}")
        applied, missed = apply_to_text(fpath, pairs)
        for a in applied:
            print(f"    ✅ {a}")
        for m in missed:
            print(f"    ⚠️  미발견: {m}")
        total_applied += len(applied)
        total_missed += len(missed)

    print(f"\n총 적용: {total_applied} / 미발견: {total_missed}")
    print("=" * 60)

    residual = verify_residual()
    return 0 if residual == 0 else 2


if __name__ == "__main__":
    sys.exit(main())