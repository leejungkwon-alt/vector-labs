# scripts/patch_guest_restore.py
"""
로그인 직전 게스트 세션을 백업하고, 로그아웃 시 그 게스트로 복원.
- 백업 키: 'saju.guest_token_backup'
- 백업은 최초 1회만 저장 (이후 로그인 시 덮어쓰지 않음)
"""
from pathlib import Path
import sys
import difflib

PATH = Path("frontend/src/store/authStore.ts")
if not PATH.exists():
    print(f"❌ 파일 없음: {PATH}"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

if "GUEST_TOKEN_BACKUP_KEY" in src:
    print("⚠️ 이미 패치되어 있습니다."); sys.exit(0)

# 1) 상수 + 헬퍼 함수 추가
old_const = "const TOKEN_KEY = 'saju.access_token';"
new_const = """const TOKEN_KEY = 'saju.access_token';
const GUEST_TOKEN_BACKUP_KEY = 'saju.guest_token_backup';

// 로그인 직전 게스트 토큰을 백업 (최초 게스트만 보존)
async function backupGuestToken(): Promise<void> {
  try {
    const existing = await storage.getItem(GUEST_TOKEN_BACKUP_KEY);
    if (existing) return;
    const current = await storage.getItem(TOKEN_KEY);
    if (current) await storage.setItem(GUEST_TOKEN_BACKUP_KEY, current);
  } catch (e) {
    console.warn('[backupGuestToken] failed:', e);
  }
}"""
if old_const not in src:
    print("❌ TOKEN_KEY 상수 못 찾음"); sys.exit(1)
src = src.replace(old_const, new_const, 1)

# 2) linkAccount 직전에 백업
old_link = """    await storage.setItem(TOKEN_KEY, res.access_token);
    setAuthToken(res.access_token);
    set({ user: res.user });
    try { await useProfileStore.getState().loadProfile(); } catch {}
  },
  signInWithProvider:"""
new_link = """    await backupGuestToken();
    await storage.setItem(TOKEN_KEY, res.access_token);
    setAuthToken(res.access_token);
    set({ user: res.user });
    try { await useProfileStore.getState().loadProfile(); } catch {}
  },
  signInWithProvider:"""
if new_link not in src:
    if old_link not in src:
        print("❌ linkAccount 부분 못 찾음"); sys.exit(1)
    src = src.replace(old_link, new_link, 1)

# 3) signInWithProvider 직전에 백업
old_login = """    const res = await api.loginProvider(provider, providerToken);
    await storage.setItem(TOKEN_KEY, res.access_token);"""
new_login = """    const res = await api.loginProvider(provider, providerToken);
    await backupGuestToken();
    await storage.setItem(TOKEN_KEY, res.access_token);"""
if new_login not in src:
    if old_login not in src:
        print("❌ signInWithProvider 부분 못 찾음"); sys.exit(1)
    src = src.replace(old_login, new_login, 1)

# 4) signOut 로직 교체
old_signout = """  signOut: async () => {
    await storage.deleteItem(TOKEN_KEY);
    setAuthToken(null);
    set({ user: null });
    // 🆕 로그아웃 후 새 익명 세션 자동 생성
    try {
      const res = await api.anonymous();
      await storage.setItem(TOKEN_KEY, res.access_token);
      setAuthToken(res.access_token);
      set({ user: res.user, ready: true, authError: null });
      try { await useProfileStore.getState().loadProfile(); } catch {}
    } catch (e) {
      console.warn('[signOut] anonymous re-issue failed:', e);
    }
  },"""
new_signout = """  signOut: async () => {
    setAuthToken(null);
    set({ user: null });
    try { await useProfileStore.getState().clearProfile(); } catch {}

    // 🆕 로그인 직전 게스트 토큰이 있으면 그 세션으로 복원
    const backup = await storage.getItem(GUEST_TOKEN_BACKUP_KEY);
    if (backup) {
      try {
        setAuthToken(backup);
        const me = await api.me();
        await storage.setItem(TOKEN_KEY, backup);
        await storage.deleteItem(GUEST_TOKEN_BACKUP_KEY);
        set({ user: me.user, ready: true, authError: null });
        try { await useProfileStore.getState().loadProfile(); } catch {}
        return;
      } catch (e) {
        console.warn('[signOut] guest restore failed, falling back:', e);
        await storage.deleteItem(GUEST_TOKEN_BACKUP_KEY);
      }
    }

    // 백업이 없거나 무효 → 새 익명 세션 생성
    try {
      await storage.deleteItem(TOKEN_KEY);
      const res = await api.anonymous();
      await storage.setItem(TOKEN_KEY, res.access_token);
      setAuthToken(res.access_token);
      set({ user: res.user, ready: true, authError: null });
      try { await useProfileStore.getState().loadProfile(); } catch {}
    } catch (e) {
      console.warn('[signOut] anonymous re-issue failed:', e);
    }
  },"""
if new_signout not in src:
    if old_signout not in src:
        print("❌ signOut 부분 못 찾음. 수동 확인 필요."); sys.exit(1)
    src = src.replace(old_signout, new_signout, 1)

# diff 미리보기
sys.stdout.writelines(difflib.unified_diff(
    PATH.read_text(encoding="utf-8").splitlines(keepends=True),
    src.splitlines(keepends=True),
    fromfile="before", tofile="after", n=2,
))

if "--apply" not in sys.argv:
    print("\n💡 dry-run. 적용: python scripts/patch_guest_restore.py --apply")
    sys.exit(0)

PATH.write_text(src, encoding="utf-8")
print("\n✅ authStore.ts 패치 완료")