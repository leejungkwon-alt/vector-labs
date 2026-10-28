"""
fix_minor_i18n.py

Minor i18n 정리 (m-1 ~ m-5):
- m-1: zh_cn pillar name의 《》 북명호 제거
- m-2: 戊申 "Rocky Mountain" 오역 정정 (zh_cn / es)
- m-3: zh_cn narrative의 로마자 필러명 → 한자
- m-4: ja/core.json DEFAULT_INTENSITY 번역
- m-5: ja/core.json element 필드 언어 통일 (Wood → 木 등)

실행:
    python fix_minor_i18n.py
    python -m pytest -q
    python scripts/verify_i18n.py
"""
import json
import pathlib
import re

DATA = pathlib.Path(__file__).resolve().parent.parent \
    / "app" / "services" / "content" / "data"


def _load(p): return json.loads(p.read_text(encoding="utf-8"))
def _save(p, d): p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ─────────────────────────────────────────────────────────
# m-1: 《》 북명호 제거
# ─────────────────────────────────────────────────────────
PILLAR_ANGLE_NAMES = {
    "丙寅": "森林之火",
    "壬午": "海火",
    "壬寅": "海与春的邂逅",
    "辛巳": "烈火中的宝玉",   # C-4에서 이미 《》 있었을 가능성
}


def fix_m1_angle_brackets() -> int:
    fixed = 0
    # 1) pillar_names.json
    p = DATA / "zh_cn" / "pillar_names.json"
    d = _load(p)
    for pillar, clean_name in PILLAR_ANGLE_NAMES.items():
        if pillar in d and d[pillar].get("name") != clean_name:
            print(f"  [FIX] pillar_names.json {pillar}: {d[pillar].get('name')!r} -> {clean_name!r}")
            d[pillar]["name"] = clean_name
            fixed += 1
    _save(p, d)

    # 2) core_pillars/*.json (개별)
    for pillar in PILLAR_ANGLE_NAMES:
        p = DATA / "zh_cn" / "core_pillars" / f"{pillar}.json"
        if not p.exists():
            continue
        d = _load(p)
        old = d.get("name", "")
        if old.startswith("《") and old.endswith("》"):
            new = old.strip("《》")
            print(f"  [FIX] core_pillars/{pillar}.json name: {old!r} -> {new!r}")
            d["name"] = new
            _save(p, d)
            fixed += 1
    return fixed


# ─────────────────────────────────────────────────────────
# m-2: 戊申 "Rocky Mountain" 오역 (북미 산맥 고유명사 → 일반명사)
# ─────────────────────────────────────────────────────────
def fix_m2_wushen() -> int:
    fixed = 0
    pairs = [
        (DATA / "zh_cn" / "pillar_names.json", "落基山脉", "岩石之山", "zh_cn/pillar_names"),
        (DATA / "zh_cn" / "core_pillars" / "戊申.json", "落基山脉", "岩石之山", "zh_cn/core_pillars/戊申"),
        (DATA / "es" / "pillar_names.json", "Montañas Rocosas", "Montaña de roca", "es/pillar_names"),
        (DATA / "es" / "core_pillars" / "戊申.json", "Montañas Rocosas", "Montaña de roca", "es/core_pillars/戊申"),
    ]
    for path, bad, good, label in pairs:
        if not path.exists():
            continue
        d = _load(path)
        target = d.get("戊申", d) if "戊申" in d else d
        if isinstance(target, dict) and target.get("name") == bad:
            print(f"  [FIX] {label}: {bad!r} -> {good!r}")
            target["name"] = good
            _save(path, d)
            fixed += 1
    return fixed


# ─────────────────────────────────────────────────────────
# m-3: zh_cn narrative 내 로마자 필러명 → 한자
# ─────────────────────────────────────────────────────────
ROMAN_TO_HANZI = {
    "Jia-Zi":  "甲子", "Jia-In":  "甲寅", "Jia-O":   "甲午", "Jia-Jin": "甲辰",
    "Jia-Shin":"甲申", "Jia-Sul": "甲戌",
    "Yi-Chou": "乙丑", "Yi-Hai":  "乙亥", "Yi-Mao":  "乙卯", "Yi-Si":   "乙巳",
    "Yi-Wei":  "乙未", "Yi-You":  "乙酉",
    "Bing-In": "丙寅", "Bing-O":   "丙午", "Bing-Jin":"丙辰", "Bing-Shin":"丙申","Bing-Sul":"丙戌",
    "Bing-Ja": "丙子",
    "Ding-Mao":"丁卯", "Ding-Si":  "丁巳", "Ding-Wei":"丁未", "Ding-You":"丁酉",
    "Ding-Chou":"丁丑","Ding-Hae": "丁亥",
    "Mu-Jin":  "戊辰", "Mu-In":   "戊寅", "Mu-O":    "戊午", "Mu-Shin": "戊申",
    "Mu-Sul":  "戊戌", "Mu-Ja":   "戊子",
    "Ji-Chou": "己丑", "Ji-Hae":  "己亥", "Ji-Mao":  "己卯", "Ji-Si":   "己巳",
    "Ji-Wei":  "己未", "Ji-You":  "己酉",
    "Geng-Ja": "庚子", "Geng-In": "庚寅", "Geng-Jin":"庚辰", "Geng-O":  "庚午",
    "Geng-Shin":"庚申","Geng-Sul":"庚戌",
    "Xin-Chou":"辛丑", "Xin-Hae": "辛亥", "Xin-Mao": "辛卯", "Xin-Si":  "辛巳",
    "Xin-Wei": "辛未", "Xin-You": "辛酉",
    "Im-Ja":   "壬子", "Im-In":   "壬寅", "Im-Jin":  "壬辰", "Im-O":    "壬午",
    "Im-Shin": "壬申", "Im-Sul":  "壬戌",
    "Gye-Chou":"癸丑", "Gye-Hae": "癸亥", "Gye-Mao": "癸卯", "Gye-Si":  "癸巳",
    "Gye-Wei": "癸未", "Gye-You": "癸酉",
}

_ROMAN_RE = re.compile(
    r"\b(?:Jia|Yi|Bing|Ding|Mu|Ji|Geng|Xin|Im|Gye)-"
    r"(?:Zi|In|O|Jin|Shin|Sul|Chou|Hae|Mao|Si|Wei|You|Ja)\b"
)


def _walk_str(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                yield obj, k, v
            else:
                yield from _walk_str(v)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, str):
                yield obj, i, v
            else:
                yield from _walk_str(v)


def fix_m3_romanized_names() -> int:
    fixed = 0
    for f in (DATA / "zh_cn").rglob("*.json"):
        d = _load(f)
        changes = []
        for container, key, value in _walk_str(d):
            new = _ROMAN_RE.sub(lambda m: ROMAN_TO_HANZI.get(m.group(0), m.group(0)), value)
            if new != value:
                container[key] = new
                changes.append(f"{f.name}:{key}: ...{value[:40]}...")
                fixed += 1
        if changes:
            _save(f, d)
            print(f"  [FIX] {f.name} ({len(changes)} substitutions)")
    return fixed


# ─────────────────────────────────────────────────────────
# m-4 + m-5: ja/core.json DEFAULT_INTENSITY + element 통일
# ─────────────────────────────────────────────────────────
JA_ELEMENT_MAP = {
    "Wood": "木", "Fire": "火", "Earth": "土",
    "Metal": "金", "Water": "水",
}
JA_DEFAULT_INTENSITY = {
    "hero": "あなたはまだ、形成されつつある存在です。",
    "narrative": [
        "このチャートは、まだ言葉にできない方法で読み解かれようとしています。"
    ],
    "shadows": [],
    "advice": [],
    "keywords": [],
}


def fix_m4_m5_ja() -> int:
    fixed = 0
    p = DATA / "ja" / "core.json"
    d = _load(p)

    # m-4: DEFAULT_INTENSITY
    if d.get("DEFAULT_INTENSITY", {}).get("hero") == "You are still becoming.":
        print("  [FIX] ja/core.json DEFAULT_INTENSITY 번역")
        d["DEFAULT_INTENSITY"] = JA_DEFAULT_INTENSITY
        fixed += 1

    # m-5: element 통일
    for arch_key, arch in d.get("ARCHETYPE_CONTENT", {}).items():
        if isinstance(arch, dict) and arch.get("element") in JA_ELEMENT_MAP:
            old = arch["element"]
            new = JA_ELEMENT_MAP[old]
            print(f"  [FIX] ja/core.json {arch_key}.element: {old!r} -> {new!r}")
            arch["element"] = new
            fixed += 1

    if fixed:
        _save(p, d)
    return fixed


if __name__ == "__main__":
    print("── m-1: 《》 북명호 제거 ──")
    n1 = fix_m1_angle_brackets()
    print("\n── m-2: 戊申 오역 ──")
    n2 = fix_m2_wushen()
    print("\n── m-3: zh_cn 로마자 → 한자 ──")
    n3 = fix_m3_romanized_names()
    print("\n── m-4+m-5: ja/core.json ──")
    n4 = fix_m4_m5_ja()
    print(f"\n완료: m-1={n1} / m-2={n2} / m-3={n3} / m-4·m-5={n4}")