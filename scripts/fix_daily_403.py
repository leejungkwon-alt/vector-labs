# scripts/fix_daily_403.py
from pathlib import Path
import sys

TARGET = Path("frontend/app/(tabs)/daily.tsx")
APPLY = "--apply" in sys.argv

if not TARGET.exists():
    print(f"❌ 파일을 찾을 수 없습니다: {TARGET}")
    sys.exit(1)

original = TARGET.read_text(encoding="utf-8")
txt = original

# 1. useQuery에 enabled 옵션 추가
old_query = 'queryFn: () => api.daily({ ...profile, days: 7, lang }),'
new_query = '''queryFn: () => api.daily({ ...profile, days: 7, lang }),
    enabled: !!user && user.tier !== "free", // 🚨 무료 회원은 API 호출하지 않음'''

if old_query in txt:
    txt = txt.replace(old_query, new_query, 1)
    print("✅ useQuery에 enabled 조건 추가 완료")
else:
    print("❌ queryFn 패턴을 찾지 못했습니다. 파일 내용을 확인해주세요.")
    sys.exit(1)

if txt == original:
    print("ℹ️ 변경 사항이 없습니다.")
    sys.exit(0)

if not APPLY:
    print("\n🧪 미리보기 모드입니다. 실제로 적용하려면 --apply 플래그를 추가하세요.")
    sys.exit(0)

TARGET.write_text(txt, encoding="utf-8")
print(f"🎉 패치 완료: {TARGET}")