import json, pathlib, re, sys

DATA = pathlib.Path("app/services/content/data")
LANGS = ["en", "ko", "ja", "zh_cn", "es"]
problems = []

# 1) 타 언어 팩에 한글/일본어/중국어/영어 문단이 섞였는지 휴리스틱 검사
def looks_english(s):
    return bool(re.search(r'\b(the|you|your|this|that|and)\b', s, re.I))

for lang in ["ja", "zh_cn", "es"]:
    for f in (DATA / lang / "core_pillars").glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        for i, p in enumerate(d.get("narrative", [])):
            if looks_english(p):
                problems.append(f"{f}: narrative[{i}] looks English")

# 2) element 필드는 木/火/土/金/水 (또는 해당 언어 정식 표기)만 허용
VALID_ELEM_ZH = {"木", "火", "土", "金", "水"}
for f in (DATA / "zh_cn").rglob("*.json"):
    d = json.loads(f.read_text(encoding="utf-8"))
    def walk(o, path=""):
        if isinstance(o, dict):
            if "element" in o and isinstance(o["element"], str):
                if o["element"] not in VALID_ELEM_ZH and o["element"] not in ("Wood","Fire","Earth","Metal","Water"):
                    problems.append(f"{f}:{path}.element={o['element']!r}")
            for k, v in o.items(): walk(v, f"{path}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o): walk(v, f"{path}[{i}]")
    walk(d)

# 3) 금지 오역 블랙리스트
BANNED = ["艾莉", "警官", "乘务员", "运营商", "发情", "Jewel en celo", "Patada", "Cuatro"]
for f in DATA.rglob("*.json"):
    txt = f.read_text(encoding="utf-8")
    for b in BANNED:
        if b in txt:
            problems.append(f"{f}: contains banned term {b!r}")

if problems:
    print("\n".join(problems))
    sys.exit(1)
print("i18n OK")