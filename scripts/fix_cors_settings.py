# scripts/fix_cors_settings.py
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
ROOT = Path(".")
patched = False

for p in ROOT.rglob("*.py"):
    if any(x in p.parts for x in ["venv", "__pycache__", "node_modules"]):
        continue
    try:
        txt = p.read_text(encoding="utf-8")
    except Exception:
        continue

    # CORSMiddleware 설정 블록 찾기
    if "CORSMiddleware" not in txt:
        continue

    original = txt
    # allow_origins=["https://gyeol-blond.vercel.app"] 를 특정 도메인으로 교체 (allow_credentials=True 와 충돌 방지)
    if 'allow_origins=["https://gyeol-blond.vercel.app"]' in txt:
        txt = txt.replace('allow_origins=["https://gyeol-blond.vercel.app"]', 'allow_origins=["https://gyeol-blond.vercel.app"]')
        patched = True
        print(f"✅ CORS allow_origins 수정: {p}")

    if txt != original:
        if APPLY:
            p.write_text(txt, encoding="utf-8")
            print(f"🎉 파일 패치 완료: {p}")
        else:
            print(f"🧪 미리보기: {p} (--apply 로 적용)")

if not patched:
    print("ℹ️ 수정할 CORS 설정을 찾지 못했거나, 이미 설정이 올바릅니다.")
if not APPLY:
    print("\n🧪 미리보기 모드입니다. 실제로 적용하려면 --apply 플래그를 추가하세요.")