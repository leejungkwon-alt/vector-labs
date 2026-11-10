# scripts/fix_logout_flow.py
"""
signOut() 마지막에 자동 익명 세션 재생성 → 로그아웃 후 앱 정상 작동
"""
import ast
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
STORE = Path("frontend/src/store/authStore.ts")

if not STORE.exists():
    print(f"❌ {STORE} 없음")
    sys.exit(1)

txt = STORE.read_text(encoding="utf-8")

# 기존 signOut 함수 찾기
OLD = '''    signOut: async () => {
      await storage.deleteItem(TOKEN_KEY);
      setAuthToken(null);
      set({ user: null });
    },'''

NEW = '''    signOut: async () => {
      await storage.deleteItem(TOKEN_KEY);
      setAuthToken(null);
      set({ user: null });
      // 🆕 로그아웃 후 새 익명 세션 자동 생성 (앱 정상 작동 유지)
      try {
        const res = await api.anonymous();
        await storage.setItem(TOKEN_KEY, res.access_token);
        setAuthToken(res.access_token);
        set({ user: res.user, ready: true, authError: null });
      } catch (e) {
        // 익명 생성 실패해도 로그아웃은 유지 (로그인 화면으로 유도)
        console.warn("[signOut] anonymous re-issue failed:", e);
      }
    },'''

if OLD not in txt:
    print("❌ signOut 패턴 못 찾음")
    print("   다음 명령으로 현재 코드 확인:")
    print("   Get-Content 'frontend/src/store/authStore.ts' | Select-String 'signOut:' -Context 0,10")
    sys.exit(1)

txt = txt.replace(OLD, NEW, 1)
print("✅ signOut 후 자동 익명 세션 재생성")

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/fix_logout_flow.py --apply")
    sys.exit(0)

STORE.write_text(txt, encoding="utf-8")
print("\n🎉 저장 완료. 다음:")
print('   git add "frontend/src/store/authStore.ts"')
print('   git commit -m "fix(auth): auto-reissue anonymous session after signOut"')
print("   git push origin main")