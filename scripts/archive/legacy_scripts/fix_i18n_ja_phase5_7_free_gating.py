#!/usr/bin/env python3
"""
Phase 5-7: JA free_gating.json (8 labels) — ja 콘텐츠팩 마감
- labels: 8 필드만 번역
- locked_hint_extra / version: 번역 X (참조 키 / 숫자)

Idempotency: en 원본과 다르면 이미 번역 → skip.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JA = ROOT / "app" / "services" / "content" / "data" / "ja" / "free_gating.json"
EN = ROOT / "app" / "services" / "content" / "data" / "en" / "free_gating.json"

LABELS_JA = {
    "cross_insight": "クロスインサイト",
    "timing":        "今の人生の流れ",
    "body":          "本文",
    "patterns":      "パターン",
    "compatibility": "相性",
    "actions":       "実践ガイド",
    "action":        "実践ガイド",
    "red_flags":     "注意サイン",
}


def main() -> int:
    ja_data = json.loads(JA.read_text(encoding="utf-8"))
    en_data = json.loads(EN.read_text(encoding="utf-8"))
    en_labels = en_data.get("labels", {})
    ja_labels = ja_data.setdefault("labels", {})

    applied = skipped = 0
    for key, ja_val in LABELS_JA.items():
        if ja_labels.get(key) == en_labels.get(key):
            ja_labels[key] = ja_val
            print(f"✅ labels.{key}: {ja_val}")
            applied += 1
        else:
            print(f"⏭️  labels.{key}: 이미 번역됨 ({ja_labels.get(key)})")
            skipped += 1

    payload = json.dumps(ja_data, ensure_ascii=False, indent=2) + "\n"
    json.loads(payload)
    JA.write_text(payload, encoding="utf-8")

    print(f"\n결과: applied={applied}, skipped={skipped}")

    # ---- 검증 ----
    print("\n[verify]")
    data = json.loads(JA.read_text(encoding="utf-8"))
    all_ok = True
    for key in LABELS_JA:
        ok = data["labels"].get(key) != en_labels.get(key)
        print(f"  {'✅' if ok else '❌'} labels.{key} = JA")
        all_ok &= ok

    lk_ok = data.get("locked_hint_extra") == en_data.get("locked_hint_extra")
    print(f"  {'✅' if lk_ok else '❌'} locked_hint_extra 원본과 동일 (번역 X)")
    all_ok &= lk_ok

    ver_ok = data.get("version") == en_data.get("version")
    print(f"  {'✅' if ver_ok else '❌'} version 원본과 동일 (숫자 유지)")
    all_ok &= ver_ok

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())