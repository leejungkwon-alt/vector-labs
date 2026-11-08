# scripts/add_get_profile_api.py
"""client.ts에 getMyProfile 메서드 추가"""
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
CLIENT = Path("frontend/src/api/client.ts")

if not CLIENT.exists():
    print(f"❌ {CLIENT} 없음")
    sys.exit(1)

txt = CLIENT.read_text(encoding="utf-8")

if "getMyProfile" in txt:
    print("ℹ️ 이미 있음")
    sys.exit(0)

# updateProfile 옆에 추가
OLD = 'updateProfile: (payload: any) => request<any>("/auth/me/profile", { method: "PUT", body: JSON.stringify(payload) }),'
NEW = 'updateProfile: (payload: any) => request<any>("/auth/me/profile", { method: "PUT", body: JSON.stringify(payload) }),\n  getMyProfile: () => request<any>("/auth/me/profile"),'

if OLD not in txt:
    print("❌ updateProfile 패턴 못 찾음")
    print("   다음 명령으로 확인:")
    print("   Get-Content 'frontend/src/api/client.ts' | Select-String 'updateProfile' -Context 0,2")
    sys.exit(1)

txt = txt.replace(OLD, NEW, 1)
print("✅ getMyProfile 추가 (GET /auth/me/profile)")

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/add_get_profile_api.py --apply")
    sys.exit(0)

CLIENT.write_text(txt, encoding="utf-8")
print(f"\n🎉 저장: {CLIENT}")