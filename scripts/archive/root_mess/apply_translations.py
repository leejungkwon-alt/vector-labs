# apply_translations.py
# 실행: python apply_translations.py translations_p0.json
#       python apply_translations.py translations_p0.json --dry-run
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "app" / "services" / "content" / "data"


def parse_path(path: str) -> list:
    import re
    tokens = []
    for part in path.split("."):
        m = re.match(r"^(\w+)((?:\[\d+\])*)$", part)
        tokens.append(m.group(1))
        for idx in re.findall(r"\[(\d+)\]", m.group(2)):
            tokens.append(int(idx))
    return tokens


def set_by_path(obj, path: str, value):
    parts = parse_path(path)
    cur = obj
    for part in parts[:-1]:
        cur = cur[part]
    cur[parts[-1]] = value


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: apply_translations.py <translations.json> [--dry-run]")
    src = Path(sys.argv[1])
    dry = "--dry-run" in sys.argv

    payload = json.loads(src.read_text(encoding="utf-8"))
    if not payload:
        sys.exit("empty payload")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = ROOT / "backups" / f"apply_{stamp}"

    for file_rel, path_map in payload.items():
        fp = DATA / file_rel
        if not fp.exists():
            print(f"[skip] {file_rel}: not found")
            continue

        data = json.loads(fp.read_text(encoding="utf-8"))
        applied = 0
        for path, translation in path_map.items():
            try:
                set_by_path(data, path, translation)
                applied += 1
            except Exception as e:
                print(f"[error] {file_rel}::{path}: {e}")

        if dry:
            print(f"[dry-run] {file_rel}: would apply {applied}")
            continue

        # 백업
        backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(fp, backup_dir / file_rel.replace("/", "__"))

        # 원자적 쓰기
        tmp = fp.with_suffix(fp.suffix + ".tmp")
        tmp.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        tmp.replace(fp)
        print(f"[applied] {file_rel}: {applied} paths → {fp}")

    print(f"\nbackup → {backup_dir}")


if __name__ == "__main__":
    main()