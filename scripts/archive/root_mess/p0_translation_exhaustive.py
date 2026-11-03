# p0_translation_exhaustive.py — 휴리스틱 없는 완전판 worklist
# 실행: python p0_translation_exhaustive.py
# 출력: p0_translation_exhaustive.json (전체) + stdout 요약
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "app" / "services" / "content" / "data"

TARGET_LANGS = ("ja", "zh_cn")
TARGET_SECTIONS = ("daily", "monthly", "year", "compatibility", "personalization")

# 한글 1자라도 있으면 "이미 번역됨"으로 간주 (ja/zh_cn 정상 항목은 한자/가나/중국어만 있어야 함)
KANA_HAN = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")
HANGUL = re.compile(r"[\uac00-\ud7af]")


def walk_strings(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_strings(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_strings(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


def is_english(s: str, min_len: int = 8) -> bool:
    """한글/가나/한자가 없고, 알파벳이 최소 min_len개 이상이면 영어로 판정."""
    if not s or len(s.strip()) < min_len:
        return False
    if KANA_HAN.search(s) or HANGUL.search(s):
        return False
    return len(re.findall(r"[A-Za-z]", s)) >= min_len


def audit():
    worklist = {}
    for lang in TARGET_LANGS:
        for section in TARGET_SECTIONS:
            fp = DATA / lang / f"{section}.json"
            if not fp.exists():
                continue
            data = json.loads(fp.read_text(encoding="utf-8"))
            hits = []
            for kp, val in walk_strings(data):
                if is_english(val):
                    hits.append({"path": kp, "len": len(val), "preview": val[:80]})
            if hits:
                worklist[f"{lang}/{section}.json"] = hits
    return worklist


def main():
    worklist = audit()
    total = sum(len(v) for v in worklist.values())

    print("=" * 70)
    print(f" 완전판 worklist — {total}개 문자열")
    print("=" * 70)
    for f, hits in sorted(worklist.items()):
        print(f"\n▶ {f} — {len(hits)}건")
        for h in hits[:8]:
            print(f"   {h['path']:<55} ({h['len']:>4}자) {h['preview'][:50]}...")
        if len(hits) > 8:
            print(f"   ... 외 {len(hits)-8}건")

    out = ROOT / "p0_translation_exhaustive.json"
    out.write_text(
        json.dumps(worklist, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\n[저장] {out.name} ({total} strings)")
    return 0


if __name__ == "__main__":
    sys.exit(main())