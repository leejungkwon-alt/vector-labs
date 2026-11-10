# scripts/fix_profile_422_and_cache.py
"""
1) 백엔드 auth.py: get_my_profile에 기본값 채우기 (422 해소)
2) 프론트 profileStore.ts: 401/422 시 캐시 삭제 (잘못된 프로필 제거)
3) 프론트 _layout.tsx: bootstrap 먼저 → loadProfile (race condition 해소)
"""
import ast
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

# ═══════════════════════════════════════════════════════════
# 1. 백엔드 auth.py: 기본값 채우기
# ═══════════════════════════════════════════════════════════
AUTH = Path("app/auth/router.py")
if not AUTH.exists():
    print(f"❌ {AUTH} 없음")
    sys.exit(1)

atxt = AUTH.read_text(encoding="utf-8")

OLD_GET = '''@router.get("/me/profile", response_model=ProfileResponse)
def get_my_profile(user: dict = Depends(get_current_user)):
    profile = get_repository().get_profile(user["id"])
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return profile'''

NEW_GET = '''@router.get("/me/profile", response_model=ProfileResponse)
def get_my_profile(user: dict = Depends(get_current_user)):
    profile = get_repository().get_profile(user["id"])
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found.")
    # 🆕 예전 프로필 (필드 누락) 방어
    d = dict(profile)
    defaults = {
        "timezone_str": "Asia/Seoul",
        "longitude": 126.978,
        "gender": "M",
        "jasi_boundary": 23,
        "correction_mode": "lmt",
    }
    for k, v in defaults.items():
        if d.get(k) is None:
            d[k] = v
    return d'''

if OLD_GET in atxt:
    atxt = atxt.replace(OLD_GET, NEW_GET, 1)
    print("✅ 백엔드: get_my_profile 기본값 채우기")
elif "예전 프로필 (필드 누락) 방어" in atxt:
    print("ℹ️ 백엔드: 이미 패치됨")
else:
    print("⚠️ 백엔드 get_my_profile 패턴 불일치")
    print("   다음 명령으로 확인:")
    print("   Get-Content 'app/auth/router.py' | Select-String 'get_my_profile' -Context 0,10")

try:
    ast.parse(atxt)
    if APPLY:
        AUTH.write_text(atxt, encoding="utf-8")
except SyntaxError as e:
    print(f"❌ 백엔드 문법 오류: {e.lineno}")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════
# 2. 프론트 profileStore.ts: 401/422 시 캐시 삭제
# ═══════════════════════════════════════════════════════════
STORE = Path("frontend/src/store/profileStore.ts")
if not STORE.exists():
    print(f"❌ {STORE} 없음")
    sys.exit(1)

stxt = STORE.read_text(encoding="utf-8")

OLD_LOAD = '''  loadProfile: async () => {
    try {
      // 1) 백엔드에서 현재 로그인 계정의 프로필 우선 조회
      try {
        const res = await api.getMyProfile();  // GET /auth/me/profile
        if (res) {
          set({ profile: res, ready: true });
          // 로컬 캐시도 동기화
          await AsyncStorage.setItem(PROFILE_KEY, JSON.stringify(res));
          return;
        }
      } catch (e: any) {
        // 404 = 아직 프로필 없음 → 캐시 시도
        // 401 = 로그인 안 됨 → 캐시 시도
        // 500/네트워크 → 캐시 fallback
      }
      // 2) 백엔드 실패 시 로컬 캐시 fallback
      const data = await AsyncStorage.getItem(PROFILE_KEY);
      if (data) {
        set({ profile: JSON.parse(data), ready: true });
      } else {
        set({ profile: null, ready: true });
      }
    } catch {
      set({ ready: true });
    }
  },'''

NEW_LOAD = '''  loadProfile: async () => {
    try {
      // 1) 백엔드에서 현재 로그인 계정의 프로필 우선 조회
      try {
        const res = await api.getMyProfile();
        if (res) {
          set({ profile: res, ready: true });
          await AsyncStorage.setItem(PROFILE_KEY, JSON.stringify(res));
          return;
        }
      } catch (e: any) {
        // 🆕 401/422 = 토큰 문제 또는 프로필 손상 → 캐시 신뢰 불가
        //         → 캐시 삭제 후 null
        if (e?.status === 401 || e?.status === 422) {
          await AsyncStorage.removeItem(PROFILE_KEY);
          set({ profile: null, ready: true });
          return;
        }
        // 404 = 신규 계정 (프로필 없음) → 캐시 시도
        // 5xx = 서버 장애 → 캐시 fallback
      }
      // 2) 백엔드 실패 시 로컬 캐시 fallback
      const data = await AsyncStorage.getItem(PROFILE_KEY);
      if (data) {
        set({ profile: JSON.parse(data), ready: true });
      } else {
        set({ profile: null, ready: true });
      }
    } catch {
      set({ ready: true });
    }
  },'''

if OLD_LOAD in stxt:
    stxt = stxt.replace(OLD_LOAD, NEW_LOAD, 1)
    print("✅ 프론트: 401/422 시 캐시 삭제")
elif "401/422 = 토큰 문제" in stxt:
    print("ℹ️ 프론트: 이미 패치됨")
else:
    print("⚠️ profileStore loadProfile 패턴 불일치")

if APPLY and stxt != STORE.read_text(encoding="utf-8"):
    STORE.write_text(stxt, encoding="utf-8")

# ═══════════════════════════════════════════════════════════
# 3. _layout.tsx: bootstrap 먼저 → loadProfile (race 해소)
# ═══════════════════════════════════════════════════════════
LAYOUT = Path("frontend/app/_layout.tsx")
if LAYOUT.exists():
    ltxt = LAYOUT.read_text(encoding="utf-8")
    OLD_BOOT = '''await Promise.all([bootstrap(), loadLang(), loadProfile()]);'''
    NEW_BOOT = '''await bootstrap();
        await Promise.all([loadLang(), loadProfile()]);'''
    if OLD_BOOT in ltxt:
        ltxt = ltxt.replace(OLD_BOOT, NEW_BOOT, 1)
        print("✅ _layout.tsx: bootstrap 먼저 (race 해소)")
        if APPLY:
            LAYOUT.write_text(ltxt, encoding="utf-8")
    elif "await bootstrap();" in ltxt:
        print("ℹ️ _layout: 이미 패치됨")
    else:
        print("⚠️ _layout bootstrap 패턴 불일치")

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/fix_profile_422_and_cache.py --apply")
    sys.exit(0)

print("\n🎉 완료. 다음 명령:")
print("   .\\deploy.ps1  (백엔드 재배포 - 422 해소)")
print('   git add "frontend/src/store/profileStore.ts" "frontend/app/_layout.tsx"')
print('   git commit -m "fix(profile): handle 422 + race condition"')
print("   git push origin main  (프론트 재배포)")