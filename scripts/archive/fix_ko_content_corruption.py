#!/usr/bin/env python3
"""
한국어 콘텐츠 손상 복원 (Step 1: 지지 → 땅의 기운 일괄 치환 사고).
- 원칙: 정확한 문자열만 타겟 치환 (전역 치환 금지 — 정당한 地支 번역 보호)
- 안전: JSON 파싱 검증 실패 시 저장 취소 + .bak 백업
- 검증: 수정 후 남은 손상 패턴 재스캔
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KO_DATA = ROOT / "app" / "services" / "content" / "data" / "ko"

REPLACEMENTS = {
    "core.json": [
        ("휘어지니까 부러땅의 기운 않는 사람이에요.",
         "휘어지니까 부러지지 않는 사람이에요."),
        ("행동으로 잘 이어땅의 기운 않을 때가 있어요.",
         "행동으로 잘 이어지지 않을 때가 있어요."),
        ("누구에게도 '잘 지내는 척'을 빚땅의 기운 않았어요.",
         "누구에게도 '잘 지내는 척'을 빚지지 않았어요."),
        ("찾으면 그 누구보다 단단해땅의 기운만, 못 찾으면 마음이 떠다닙니다.",
         "찾으면 그 누구보다 단단해지지만, 못 찾으면 마음이 떠다닙니다."),
        ('"keywords": ["양육", "실용", "꾸준함", "땅의 기운"]',
         '"keywords": ["양육", "실용", "꾸준함", "지지"]'),
        ("아직 채워땅의 기운 않은 흐름입니다.",
         "아직 채워지지 않은 흐름입니다."),
    ],
    "love.json": [
        ("조용히 당신을 땅의 기운하며 흔들릴 때",
         "조용히 당신을 지지하며 흔들릴 때"),
    ],
    "daily.json": [
        ("무기력함에 빠땅의 기운 않도록 주의하세요.",
         "무기력함에 빠지지 않도록 주의하세요."),
    ],
    "compatibility.json": [
        ("두 사람의 비즈니스 케미은 명확한",
         "두 사람의 비즈니스 케미는 명확한"),
        ("동등한 땅의 기운와 솔직한 소통은",
         "동등한 지지와 솔직한 소통은"),
        ("이 무조건적인 땅의 기운와 깊은 이해는",
         "이 무조건적인 지지와 깊은 이해는"),
    ],
}

# 손상 후 잔존 검출용 패턴 (수정 후 이 패턴들이 남아있으면 실패)
RESIDUAL_PATTERNS = [
    "땅의 기운하", "땅의 기운해", "땅의 기운할", "땅의 기운한",
    "땅의 기운와",
    "부러땅의 기운", "이어땅의 기운", "채워땅의 기운",
    "빚땅의 기운", "빠땅의 기운", "단단해땅의 기운",
    "케미은",
]


def apply_replacements(filepath: Path, pairs):
    text = filepath.read_text(encoding="utf-8")
    original = text
    applied, missed = [], []

    for old, new in pairs:
        if old in text:
            text = text.replace(old, new)
            applied.append(old[:40])
        else:
            missed.append(old[:40])

    if text != original:
        try:
            json.loads(text)
        except json.JSONDecodeError as e:
            print(f"  ❌ {filepath.name}: JSON 파싱 실패 → 저장 취소 ({e})")
            return [], missed + ["(JSON invalid, not saved)"]
        bak = filepath.with_suffix(filepath.suffix + ".bak")
        bak.write_text(original, encoding="utf-8")
        filepath.write_text(text, encoding="utf-8")

    return applied, missed


def scan_residual(filepath: Path):
    text = filepath.read_text(encoding="utf-8")
    return [p for p in RESIDUAL_PATTERNS if p in text]


def main() -> int:
    if not KO_DATA.exists():
        print(f"❌ {KO_DATA} 없음")
        return 1

    total_applied = total_missed = 0

    for filename, pairs in REPLACEMENTS.items():
        filepath = KO_DATA / filename
        if not filepath.exists():
            print(f"\n⚠️  {filename} 없음 — 건너뜀")
            continue

        print(f"\n📄 {filename}")
        applied, missed = apply_replacements(filepath, pairs)
        for a in applied:
            print(f"  ✅ {a}")
        for m in missed:
            print(f"  ⚠️  미발견: {m}")
        total_applied += len(applied)
        total_missed += len(missed)

    print("\n" + "=" * 60)
    print(f"총 적용: {total_applied}건 / 미발견: {total_missed}건")
    print("=" * 60)

    print("\n[검증] 잔존 손상 패턴 스캔")
    any_remaining = False
    for filename in REPLACEMENTS:
        filepath = KO_DATA / filename
        if not filepath.exists():
            continue
        remaining = scan_residual(filepath)
        if remaining:
            any_remaining = True
            print(f"  ❌ {filename}: {remaining}")
        else:
            print(f"  ✅ {filename}: 깨끗")

    return 0 if not any_remaining else 2


if __name__ == "__main__":
    sys.exit(main())