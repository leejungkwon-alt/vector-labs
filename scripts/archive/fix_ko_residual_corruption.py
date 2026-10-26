#!/usr/bin/env python3
"""
ko JSON 잔존 '지지→땅의 기운' 손상 스캔 및 자동 수정.
- DRY RUN 기본 (인자 없이 실행) → 발견 항목만 나열
- --apply 로 실제 저장 (백업 + JSON 검증)
- Ambiguous 케이스는 자동 수정하지 않고 보고만 (수동 검토)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KO_DATA = ROOT / "app/services/content/data/ko"

# ─────────────────────────────────────────────────────────────
# AUTO_FIX: '땅의 기운' 뒤에 오는 문법 요소가 '지지'에만 성립
# (기운+와/는/를/가/로 등은 한국어에서 성립하지 않음 → 확실히 손상)
# ─────────────────────────────────────────────────────────────
AUTO_FIX = {
    # 지지 + 동사 어미
    "땅의 기운하": "지지하",
    "땅의 기운해": "지지해",
    "땅의 기운할": "지지할",
    "땅의 기운한": "지지한",
    "땅의 기운했": "지지했",
    "땅의 기운합": "지지합",
    "땅의 기운면": "지지면",
    "땅의 기운면서": "지지면서",
    "땅의 기운고": "지지고",
    "땅의 기운든": "지지든",
    "땅의 기운라": "지지라",
    # 지지 + 조사 (기운+조사는 모음/받침 규칙상 성립 불가)
    "땅의 기운와": "지지와",
    "땅의 기운는": "지지는",
    "땅의 기운를": "지지를",
    "땅의 기운가": "지지가",
    "땅의 기운로": "지지로",
    # 어간 + 지지 복합 (지지→땅의 기운 일괄 치환 잔재)
    "부러땅의 기운": "부러지지",
    "이어땅의 기운": "이어지지",
    "채워땅의 기운": "채워지지",
    "빚땅의 기운": "빚지지",
    "빠땅의 기운": "빠지지",
    "단단해땅의 기운": "단단해지지",
    "가땅의 기운": "가지지",
    # 별건 손상
    "케미은": "케미는",
}

# ─────────────────────────────────────────────────────────────
# AMBIGUOUS: '땅의 기운' 뒤에 오는 요소가 정상 한국어일 수도 있는 경우
# 예: '땅의 기운도' (지지도 or 기운도) — 자동 수정 금지, 사람이 판단
# ─────────────────────────────────────────────────────────────
AMBIGUOUS = [
    "땅의 기운도", "땅의 기운에", "땅의 기운의",
    "땅의 기운만", "땅의 기운과", "땅의 기운이",
    "땅의 기운을", "땅의 기운은", "땅의 기운으로",
]


def iter_strings(node, path="root"):
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from iter_strings(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from iter_strings(v, f"{path}[{i}]")


def main() -> int:
    dry_run = "--apply" not in sys.argv
    print(f"Mode: {'DRY RUN (--apply 로 저장)' if dry_run else 'APPLY'}\n")

    fixes = []       # (file, jsonpath, pat, repl, ctx)
    ambiguous = []   # (file, jsonpath, pat, ctx)

    for f in sorted(KO_DATA.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        for jsonpath, text in iter_strings(data):
            for pat, repl in AUTO_FIX.items():
                idx = 0
                while True:
                    pos = text.find(pat, idx)
                    if pos == -1:
                        break
                    ctx = text[max(0, pos - 25):pos + len(pat) + 25]
                    fixes.append((f, jsonpath, pat, repl, ctx))
                    idx = pos + 1
            for pat in AMBIGUOUS:
                if pat in text:
                    pos = text.find(pat)
                    ctx = text[max(0, pos - 30):pos + len(pat) + 30]
                    ambiguous.append((f, jsonpath, pat, ctx))

    # ── 보고
    if fixes:
        print(f"🔧 AUTO-FIX 대상 {len(fixes)}건\n")
        for f, jsonpath, pat, repl, ctx in fixes:
            print(f"  📄 {f.name}  ::  {jsonpath}")
            print(f"     '{pat}' → '{repl}'")
            print(f"     …{ctx}…\n")
    else:
        print("✅ AUTO-FIX 대상 없음")

    if ambiguous:
        print(f"\n⚠️  AMBIGUOUS {len(ambiguous)}건 (수동 검토 필요)\n")
        for f, jsonpath, pat, ctx in ambiguous:
            print(f"  📄 {f.name}  ::  {jsonpath}")
            print(f"     '{pat}'  …{ctx}…")

    if dry_run or not fixes:
        return 0 if not fixes else 1

    # ── 적용
    print("\n" + "=" * 60 + "\nAPPLYING...\n")
    for f in sorted(set(x[0] for x in fixes)):
        text = f.read_text(encoding="utf-8")
        original = text
        for pat, repl in AUTO_FIX.items():
            text = text.replace(pat, repl)
        if text == original:
            continue
        try:
            json.loads(text)
        except json.JSONDecodeError as e:
            print(f"  ❌ {f.name}: JSON invalid → skip ({e})")
            continue
        (f.parent / (f.name + ".bak.residual")).write_text(original, encoding="utf-8")
        f.write_text(text, encoding="utf-8")
        print(f"  ✅ {f.name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())