import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN_PY = ROOT / "app" / "main.py"
SUFFIX = f".bak_cors_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def main():
    text = MAIN_PY.read_text(encoding="utf-8")
    
    old_regex = 'allow_origin_regex=r"https://.*\\.vercel\\.app",'
    # localhost와 127.0.0.1(모든 포트) 및 기존 vercel 도메인 허용
    new_regex = 'allow_origin_regex=r"https?://(localhost|127\\.0\\.0\\.1)(:\\d+)?|https://.*\\.vercel\\.app",'

    if new_regex in text:
        print("[SKIP] CORS already patched.")
        return

    if text.count(old_regex) != 1:
        print("[ERR] CORS anchor not found or not unique.")
        sys.exit(1)

    bak = MAIN_PY.with_name(MAIN_PY.name + SUFFIX)
    shutil.copy2(MAIN_PY, bak)
    print(f"[backup] {bak.name}")

    text = text.replace(old_regex, new_regex)
    MAIN_PY.write_text(text, encoding="utf-8")
    print("[OK] main.py CORS patched! (now allows localhost)")

if __name__ == "__main__":
    main()