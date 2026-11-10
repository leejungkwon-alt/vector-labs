# scripts/fix_logout_complete.py
"""
로그아웃 완벽 처리:
1) settings.tsx: signOut 후 clearProfile() + 웹은 풀 리로드
2) authStore.ts: signOut에 loadProfile 대신 명시적 clearProfile
"""
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

# ═══════════════════════════════════════════════════════════
# 1. settings.tsx: clearProfile + 풀 리로드
# ═══════════════════════════════════════════════════════════
SETTINGS = Path("frontend/app/(tabs)/settings.tsx")
if not SETTINGS.exists():
    print(f"❌ {SETTINGS} 없음")
    sys.exit(1)

txt = SETTINGS.read_text(encoding="utf-8")
orig = txt

OLD = '''  const handleSignOut = async () => {
    const performSignOut = async () => {
      try {
        await signOut();
        router.replace("/");
      } catch (e: any) {
        const msg = e?.message || t("settings.logoutFail");
        if (Platform.OS === "web") alert(msg);
        else Alert.alert(t("common.notice"), msg);
      }
    };'''

NEW = '''  const handleSignOut = async () => {
    const performSignOut = async () => {
      try {
        await signOut();
        // 🆕 프로필/시조 상태 완전 초기화 (이전 계정 데이터 제거)
        try { await clearProfile(); } catch {}
        try { setCurrentPoem(null as any, []); } catch {}
        // 🆕 웹은 풀 리로드 (모든 캐시 초기화, 확실한 로그아웃)
        if (Platform.OS === "web") {
          window.location.href = "/";
        } else {
          router.replace("/");
        }
      } catch (e: any) {
        const msg = e?.message || t("settings.logoutFail");
        if (Platform.OS === "web") alert(msg);
        else Alert.alert(t("common.notice"), msg);
      }
    };'''

if OLD not in txt:
    print("❌ settings.tsx handleSignOut 패턴 못 찾음")
    print("   다음 명령으로 확인:")
    print("   Get-Content 'frontend/app/(tabs)/settings.tsx' | Select-String 'handleSignOut' -Context 0,15")
    sys.exit(1)

txt = txt.replace(OLD, NEW, 1)
print("✅ settings.tsx: clearProfile + 풀 리로드 추가")

# poemStore import 확인
if "usePoemStore" not in txt:
    # import 추가
    txt = txt.replace(
        'import { useProfileStore } from "@/store/profileStore";',
        'import { useProfileStore } from "@/store/profileStore";\nimport { usePoemStore } from "@/store/poemStore";',
        1,
    )
    print("✅ usePoemStore import 추가")

# setCurrentPoem 훅 추가
if "setCurrentPoem = usePoemStore" not in txt:
    # clearProfile 옆에 추가
    txt = txt.replace(
        'const clearProfile = useProfileStore((s) => s.clearProfile);',
        'const clearProfile = useProfileStore((s) => s.clearProfile);\n  const setCurrentPoem = usePoemStore((s) => s.setCurrentPoem);',
        1,
    )
    print("✅ setCurrentPoem 훅 추가")

if txt == orig:
    print("ℹ️ 변경 사항 없음")
    sys.exit(0)

# 괄호 검증
if txt.count("{") != txt.count("}"):
    print(f"❌ 중괄호 불균형")
    sys.exit(1)

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/fix_logout_complete.py --apply")
    sys.exit(0)

SETTINGS.write_text(txt, encoding="utf-8")
print(f"\n🎉 저장: {SETTINGS}")
print("\n다음:")
print('   git add "frontend/app/(tabs)/settings.tsx"')
print('   git commit -m "fix(auth): complete logout - clear profile + full reload"')
print("   git push origin main")