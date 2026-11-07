# scripts/dump_interpretations.py
"""data/poems.json의 25개 시조 interpretation을 보기 좋게 덤프."""
import json
from pathlib import Path

POEMS = Path("data/poems.json")
data = json.load(POEMS.open(encoding="utf-8"))
poems = data.get("poems", [])

RELATION_KR = {
    "same": "同 (같은 기운)",
    "generates_me": "生我 (나를 낳아줌)",
    "i_generate": "我生 (내가 낳음)",
    "i_control": "我剋 (내가 극함)",
    "controls_me": "剋我 (나를 극함)",
}
ELEM_KR = {"木": "목(성장)", "火": "화(열정)", "土": "토(안정)", "金": "금(결단)", "水": "수(유연)"}

print(f"📖 data/poems.json — 총 {len(poems)}개 시조\n")

# 한국어 먼저 (재작성 기준이 됨)
print("=" * 70)
print("🇰🇷 한국어 interpretation 전체 (재작성 대상)")
print("=" * 70)
for p in poems:
    pid = p.get("id", "?")
    elem = p.get("element", "?")
    rel = p.get("relation", "?")
    tr = (p.get("translations") or {}).get("ko") or {}
    interp = tr.get("interpretation", "(없음)")
    sijo = p.get("sijo_ko", "")
    
    print(f"\n[{pid}]  {ELEM_KR.get(elem, elem)} × {RELATION_KR.get(rel, rel)}")
    print(f"  시조: {sijo.replace(chr(10), ' / ')}")
    print(f"  현재: {interp}")

# 영어 interpretation도 참고용
print("\n" + "=" * 70)
print("🇺🇸 영어 interpretation 전체")
print("=" * 70)
for p in poems:
    pid = p.get("id", "?")
    tr = (p.get("translations") or {}).get("en") or {}
    interp = tr.get("interpretation", "(없음)")
    print(f"\n[{pid}]")
    print(f"  {interp}")