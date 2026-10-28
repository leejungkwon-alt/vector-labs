"""verify_i18n.py — i18n 회귀 방지 (JSON-aware, exact-match, romanized-pillar 제외)."""
import json
import pathlib
import re
import sys

DATA = pathlib.Path(__file__).resolve().parent.parent \
    / "app" / "services" / "content" / "data"

problems: list[str] = []


def _walk_paths(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk_paths(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk_paths(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


# ── 1) narrative 안 영어 검사 (로마자 필러 제거 후) ──
# 로마자 필러명: Ding-You, Geng-Jin, Yi-Hai, Mu-Jin, Gye-You 등
_ROMAN_PILLAR = re.compile(
    r"\b(?:Ding|Yi|Ji|Gye|Xin|Byung|Jung|Mu|Ki|Kyung|Shin|Im|Geng|"
    r"Bing|Wu|Jia|Gui|Ren|Geng)[-\s]"
    r"(?:You|Jin|In|Chuk|Hae|Myo|Sa|O|Mi|Shin|Yu|Sul|Ja|Chuk)\b",
    re.I,
)
_EN_RE = re.compile(r"\b(the|you|your|this|that|and)\b", re.I)


def looks_english(s: str) -> bool:
    cleaned = _ROMAN_PILLAR.sub(" ", s)
    return bool(_EN_RE.search(cleaned))


for lang in ("ja", "zh_cn", "es"):
    base = DATA / lang / "core_pillars"
    if not base.exists():
        continue
    for f in base.glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        for i, p in enumerate(d.get("narrative", [])):
            if isinstance(p, str) and looks_english(p):
                problems.append(f"{f.relative_to(DATA)}: narrative[{i}] looks English")


# ── 2) element 필드 값 검증 (정확 매칭) ──
VALID_ZH = {"木", "火", "土", "金", "水"}
VALID_ES = {"Madera", "Fuego", "Tierra", "Metal", "Agua"}
for lang, valid in (("zh_cn", VALID_ZH), ("es", VALID_ES)):
    for f in (DATA / lang).rglob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        for path, v in _walk_paths(d):
            if path.endswith(".element") and v not in valid:
                problems.append(f"{f.relative_to(DATA)}:{path}={v!r}")


# ── 3) 금지 오역 (exact value match only) ──
BANNED_EXACT = {
    "艾莉", "警官", "乘务员", "运营商",
    "发情", "Jewel en celo", "Patada", "Cuatro",
}
for f in DATA.rglob("*.json"):
    d = json.loads(f.read_text(encoding="utf-8"))
    for path, v in _walk_paths(d):
        if v in BANNED_EXACT:
            problems.append(f"{f.relative_to(DATA)}:{path}={v!r} (banned)")


# ── 4) MODE_DISPLAY 커버리지 ──
_REQUIRED_MODES = {
    "THE_PIONEER", "THE_ADAPTER", "THE_RADIATOR", "THE_KEEPER",
    "THE_ANCHOR", "THE_CULTIVATOR", "THE_BLADE", "THE_GEM",
    "THE_DEEP", "THE_SPRING", "THE_STEWARD", "THE_OPERATOR", "THE_FLOW",
    "THE_CREATOR", "THE_CHALLENGER", "THE_OFFICER", "THE_SURVIVOR",
    "THE_MYSTIC", "THE_MENTOR", "THE_GENERALIST",
    "THE_TWIN", "THE_RIVAL", "THE_ALLY", "THE_EMPATH",
}
for lang in ("zh_cn", "es"):
    p = DATA / lang / "sections.json"
    if not p.exists():
        continue
    md = json.loads(p.read_text(encoding="utf-8")).get("MODE_DISPLAY", {})
    if missing := _REQUIRED_MODES - set(md.keys()):
        problems.append(f"{p.relative_to(DATA)}:MODE_DISPLAY missing {sorted(missing)}")


if problems:
    print("\n".join(problems))
    print(f"\n{len(problems)} problems found.")
    sys.exit(1)
print("i18n OK")