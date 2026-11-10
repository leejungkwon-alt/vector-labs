# scripts/patch_daily_tsx_enabled.py
from pathlib import Path
import sys

PATH = Path("frontend/app/(tabs)/daily.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

old_code = '''    enabled: !!user && user.tier !== "free", // 🚨 무료 회원은 API 호출하지 않음
    enabled: !!profile && profileReady && !!user && ready,'''

new_code = '''    enabled: !!profile && profileReady && !!user && ready && user.tier !== "free", // 🚨 무료 회원은 API 호출하지 않음'''

if new_code in src:
    print("⚠️ 이미 수정됨"); sys.exit(0)
if old_code not in src:
    print("❌ 대상 코드를 찾을 수 없음. 수동 확인 필요."); sys.exit(1)

PATH.write_text(src.replace(old_code, new_code, 1), encoding="utf-8")
print("✅ daily.tsx enabled 조건 통합 완료")