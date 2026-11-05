# p0_audit_translations.py — ja/zh_cn 번역 잔존 영어 감사
# 실행: python p0_audit_translations.py
# 출력: p0_translation_worklist.json (기계용) + stdout(사람용 요약)
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "app" / "services" / "content" / "data"

TARGET_LANGS = ("ja", "zh_cn")
TARGET_SECTIONS = ("daily", "monthly", "year", "compatibility", "personalization")

# 영어 stopword 2개 이상 + ASCII 비율 55% 이상 → 영어로 판정
EN_STOP = re.compile(
    r"\b(the|you|your|yours|and|with|that|this|these|those|for|from|"
    r"have|has|had|are|was|were|will|would|can|could|should|not|but|"
    r"about|into|which|they|their|them|there|when|where|what|how|why|"
    r"who|because|while|though|is|be|been|being|do|does|did)\b",
    re.IGNORECASE,
)


def walk_strings(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_strings(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_strings(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


def looks_english(s: str) -> bool:
    if len(s) < 30:
        return False
    ascii_letters = sum(1 for c in s if c.isascii() and c.isalpha())
    if ascii_letters / max(len(s), 1) < 0.55:
        return False
    stop_count = len({m.group(1).lower() for m in EN_STOP.finditer(s)})
    return stop_count >= 2


def audit():
    worklist = defaultdict(list)
    for lang in TARGET_LANGS:
        for section in TARGET_SECTIONS:
            fp = DATA / lang / f"{section}.json"
            if not fp.exists():
                continue
            data = json.loads(fp.read_text(encoding="utf-8"))
            hits = []
            for kp, val in walk_strings(data):
                if looks_english(val):
                    hits.append({"path": kp, "preview": val[:60]})
            if hits:
                worklist[f"{lang}/{section}.json"] = hits
    return worklist


def main():
    worklist = audit()

    total = sum(len(v) for v in worklist.values())
    print("=" * 70)
    print(f" 번역 잔존 감사 — {total}개 문자열 (ja/zh_cn 5개 파일)")
    print("=" * 70)

    for f, hits in sorted(worklist.items()):
        print(f"\n▶ {f} — {len(hits)}건")
        for h in hits[:5]:
            print(f"   {h['path']:<40} {h['preview']}...")
        if len(hits) > 5:
            print(f"   ... 외 {len(hits) - 5}건")

    out = ROOT / "p0_translation_worklist.json"
    out.write_text(
        json.dumps(worklist, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\n[저장] {out.name} — 번역 파이프라인/작업 분배에 사용")

    if total == 0:
        print("\n✔ 잔존 영어 없음. P0 완료.")
        return 0
    print(f"\n⚠ {total}건 — Step 3 번역 필요 (다음 단계 참조)")
    return 1


if __name__ == "__main__":
    sys.exit(main())