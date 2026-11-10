# scripts/fix_profile_backend.py
"""
profileStore.ts의 loadProfile을 백엔드 API 우선으로 수정.
- 로그인 상태면 /auth/me/profile 호출
- 실패 시 로컬 캐시 fallback
"""
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
STORE = Path("frontend/src/store/profileStore.ts")

if not STORE.exists():
    print(f"❌ {STORE} 없음")
    sys.exit(1)

txt = STORE.read_text(encoding="utf-8")

# ─── import 확인 ───
if "from \"@/api/client\"" not in txt and "from '../api/client'" not in txt:
    # import 추가
    lines = txt.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.startswith("import"):
            continue
        lines.insert(i, 'import { api } from "@/api/client";\n')
        txt = "".join(lines)
        print("✅ api import 추가")
        break

# ─── loadProfile 교체 ───
OLD = '''  loadProfile: async () => {
    try {
      const data = await AsyncStorage.getItem(PROFILE_KEY);
      if (data) {
        set({ profile: JSON.parse(data), ready: true });
      } else {
        set({ ready: true });
      }
    } catch {
      set({ ready: true });
    }
  },'''

NEW = '''  loadProfile: async () => {
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

if OLD not in txt:
    print("❌ loadProfile 패턴 못 찾음")
    print("   다음 명령으로 확인:")
    print("   Get-Content 'frontend/src/store/profileStore.ts' | Select-String 'loadProfile' -Context 0,15")
    sys.exit(1)

txt = txt.replace(OLD, NEW, 1)
print("✅ loadProfile: 백엔드 우선 + 캐시 fallback")

# 괄호 검증
if txt.count("{") != txt.count("}"):
    print("❌ 중괄호 불균형")
    sys.exit(1)

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/fix_profile_backend.py --apply")
    sys.exit(0)

STORE.write_text(txt, encoding="utf-8")
print(f"\n🎉 저장: {STORE}")
print("\n다음:")
print('   git add "frontend/src/store/profileStore.ts"')
print('   git commit -m "fix(profile): load from backend first, cache as fallback"')
print("   git push origin main")