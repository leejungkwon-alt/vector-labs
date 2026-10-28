"""남은 영어 narrative 문단을 정확한 문자열로 추출."""
import json
import pathlib
import re

DATA = (pathlib.Path(__file__).resolve().parent.parent
        / "app" / "services" / "content" / "data")

def looks_english(s: str) -> bool:
    return bool(re.search(r'\b(the|you|your|this|that|and)\b', s, re.I))

result = {}
for lang in ("zh_cn", "es"):
    for f in sorted((DATA / lang / "core_pillars").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for i, p in enumerate(d.get("narrative", [])):
            if looks_english(p):
                result[f"{lang}/{f.stem}[{i}]"] = p

out = pathlib.Path(__file__).resolve().parent / "_todo_english_narratives.json"
out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Extracted {len(result)} English paragraphs -> {out}")