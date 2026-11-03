# check_placeholders.py — 번역 결과가 원본의 {placeholder}를 정확히 보존했는지 확인
# 실행: python check_placeholders.py translations_p0.json
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "app" / "services" / "content" / "data"
PH = re.compile(r"\{[a-zA-Z_][a-zA-Z0-9_]*\}")


def get_by_path(obj, path):
    for part in re.findall(r"\w+|\[\d+\]", path):
        if part.startswith("["):
            obj = obj[int(part[1:-1])]
        else:
            obj = obj[part]
    return obj


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: check_placeholders.py translations_p0.json")
    payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

    errors = 0
    for file_rel, path_map in payload.items():
        original = json.loads((DATA / file_rel).read_text(encoding="utf-8"))
        for path, translated in path_map.items():
            orig = get_by_path(original, path)
            orig_ph = set(PH.findall(orig)) if isinstance(orig, str) else set()
            tr_ph = set(PH.findall(translated))
            if orig_ph != tr_ph:
                print(f"✗ {file_rel}::{path}")
                print(f"    orig: {sorted(orig_ph)}")
                print(f"    tr  : {sorted(tr_ph)}")
                print(f"    translated: {translated[:80]}")
                errors += 1

    print(f"\n{errors} placeholder mismatch(es)")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())