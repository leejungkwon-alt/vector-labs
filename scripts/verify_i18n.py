"""verify_i18n.py — i18n 회귀 방지 (JSON-aware exact-value match)."""
import json
import pathlib
import re
import sys

DATA = pathlib.Path(__file__).resolve().parent.parent \
    / "app" / "services" / "content" / "data"

problems: list[str] = []


def _walk_strings(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _walk_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_strings(v)
    elif isinstance(obj, str):
        yield obj


def _walk_paths(obj, path=""):
    """(json_path, value) 형태로 모든 leaf 문자열을 순회."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk_paths(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk_paths(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


# ── 1) narrative 안에 영어 문장이 섞여 있는지 (Word boundary) ──
_EN_RE = re.compile(r"\b(the|you|your|this|that|and)\b", re.I)
for lang in ("ja", "zh_cn", "es"):
    base = DATA / lang / "core_pillars"
    if not base.exists():
        continue
    for f in base.glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        for i, p in enumerate(d.get("narrative", [])):
            if isinstance(p, str) and _EN_RE.search(p):
                problems.append(f"{f.relative_to(DATA)}: narrative[{i}] looks English")


# ── 2) element 필드 값 검증 (정확 매칭) ──
VALID_ZH = {"木", "火", "土", "金", "水"}
VALID_ES = {"Madera", "Fuego", "Tierra", "Metal", "Agua"}
for f in (DATA / "zh_cn").rglob("*.json"):
    d = json.loads(f.read_text(encoding="utf-8"))
    for path, v in _walk_paths(d):
        if path.endswith(".element") and v not in VALID_ZH:
            problems.append(f"{f.relative_to(DATA)}:{path}={v!r} (not in {VALID_ZH})")
for f in (DATA / "es").rglob("*.json"):
    d = json.loads(f.read_text(encoding="utf-8"))
    for path, v in _walk_paths(d):
        if path.endswith(".element") and v not in VALID_ES:
            problems.append(f"{f.relative_to(DATA)}:{path}={v!r} (not in {VALID_ES})")


# ── 3) 금지 오역 (정확 값 매칭 only — 부분 문자열 X) ──
BANNED_EXACT = {
    "艾莉", "警官", "乘务员", "运营商",
    "发情",                    # 단독 값일 때만 (예: pillar name)
    "Jewel en celo", "Patada", "Cuatro",
}
for f in DATA.rglob("*.json"):
    d = json.loads(f.read_text(encoding="utf-8"))
    for path, v in _walk_paths(d):
        if v in BANNED_EXACT:
            problems.append(f"{f.relative_to(DATA)}:{path}={v!r} (banned)")


# ── 4) MODE_DISPLAY 커버리지 (zh_cn, es) ──
_REQUIRED_MODES = {
    "THE_PIONEER", "THE_ADAPTER", "THE_RADIATOR", "THE_KEEPER",
    "THE_ANCHOR", "THE_CULTIVATOR", "THE_BLADE", "THE_GEM",
    "THE_DEEP", "THE_SPRING",
    "THE_STEWARD", "THE_OPERATOR", "THE_FLOW",
    "THE_CREATOR", "THE_CHALLENGER", "THE_OFFICER", "THE_SURVIVOR",
    "THE_MYSTIC", "THE_MENTOR", "THE_GENERALIST",
    "THE_TWIN", "THE_RIVAL", "THE_ALLY", "THE_EMPATH",
}
for lang in ("zh_cn", "es"):
    p = DATA / lang / "sections.json"
    if not p.exists():
        continue
    d = json.loads(p.read_text(encoding="utf-8"))
    md = d.get("MODE_DISPLAY", {})
    missing = _REQUIRED_MODES - set(md.keys())
    if missing:
        problems.append(f"{p.relative_to(DATA)}:MODE_DISPLAY missing {sorted(missing)}")


if problems:
    for p in problems:
        print(p)
    print(f"\n{len(problems)} problems found.")
    sys.exit(1)
print("i18n OK")