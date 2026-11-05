#!/usr/bin/env python3
"""Phase 4-14 후속: 戊申.name 순한자 → 카나 포함. core_pillars/戊申.json과 일관성 확인."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
JA_NAMES = ROOT / "app" / "services" / "content" / "data" / "ja" / "pillar_names.json"
JA_CORE  = ROOT / "app" / "services" / "content" / "data" / "ja" / "core_pillars" / "戊申.json"
KANA_RE = re.compile(r'[\u3040-\u30FF]')

def _has_kana(s: str) -> bool:
    return bool(s) and bool(KANA_RE.search(s))

def main() -> int:
    # 1) core_pillars/戊申.json 참고 (일관성)
    core_name = ""
    if JA_CORE.exists():
        try:
            core_name = json.loads(JA_CORE.read_text(encoding="utf-8")).get("name", "")
            print(f"[info] core_pillars/戊申.name = {core_name!r} (kana={'yes' if _has_kana(core_name) else 'no'})")
        except Exception as e:
            print(f"[warn] core read fail: {e}")

    # 2) pillar_names.json 수정
    data = json.loads(JA_NAMES.read_text(encoding="utf-8"))
    old = data.get("戊申", {}).get("name", "")
    # core가 kana 포함이면 그걸 사용, 아니면 "岩の山"
    new = core_name if _has_kana(core_name) else "岩の山"
    data["戊申"]["name"] = new
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(payload)
    JA_NAMES.write_text(payload, encoding="utf-8")
    print(f"✅ 戊申.name: {old!r} → {new!r}")

    # 3) 60개 전체 재검증
    print("\n[verify]")
    bad = []
    for hanzi, d in data.items():
        if not _has_kana(d.get("name", "")):
            bad.append((hanzi, "name", d.get("name")))
        if not _has_kana(d.get("traditional", "")):
            bad.append((hanzi, "traditional", d.get("traditional")))
    if bad:
        for h, k, v in bad:
            print(f"  [ERR] {h}.{k} = {v!r}")
        return 1
    print(f"  [OK] pillar_names 60/60 = JA 🏆")
    return 0

if __name__ == "__main__":
    sys.exit(main())