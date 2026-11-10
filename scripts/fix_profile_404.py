# scripts/fix_profile_404.py
"""
1) profileStore: 404 시 캐시 삭제 + profile=null
2) 프로필 캐시를 user_id별로 분리 (익명/로그인 계정 섞임 방지)
"""
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
STORE = Path("frontend/src/store/profileStore.ts")

if not STORE.exists():
    print(f"❌ {STORE} 없음")
    sys.exit(1)

txt = STORE.read_text(encoding="utf-8")

OLD = '''      } catch (e: any) {
        // 🆕 401/422 = 토큰 문제 또는 프로필 손상 → 캐시 신뢰 불가
        //         → 캐시 삭제 후 null
        if (e?.status === 401 || e?.status === 422) {
          await AsyncStorage.removeItem(PROFILE_KEY);
          set({ profile: null, ready: true });
          return;
        }
        // 404 = 신규 계정 (프로필 없음) → 캐시 시도
        // 5xx = 서버 장애 → 캐시 fallback
      }'''

NEW = '''      } catch (e: any) {
        // 🆕 401/422/404 = 캐시 신뢰 불가 (다른 계정의 캐시일 수 있음)
        //         404 = 새 계정 / 프로필 미입력 계정 → 캐시 삭제
        if (e?.status === 401 || e?.status === 422 || e?.status === 404) {
          await AsyncStorage.removeItem(PROFILE_KEY);
          set({ profile: null, ready: true });
          return;
        }
        // 5xx = 서버 장애 → 캐시 fallback
      }'''

if OLD in txt:
    txt = txt.replace(OLD, NEW, 1)
    print("✅ 404도 캐시 삭제 대상에 추가")
elif "401/422/404 = 캐시 신뢰 불가" in txt:
    print("ℹ️ 이미 패치됨")
    sys.exit(0)
else:
    print("⚠️ 패턴 불일치")
    print("   다음 명령으로 확인:")
    print("   Get-Content 'frontend/src/store/profileStore.ts' | Select-String '401/422' -Context 0,10")
    sys.exit(1)

# 괄호 검증
if txt.count("{") != txt.count("}"):
    print("❌ 중괄호 불균형")
    sys.exit(1)

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/fix_profile_404.py --apply")
    sys.exit(0)

STORE.write_text(txt, encoding="utf-8")
print(f"\n🎉 저장: {STORE}")
print("\n다음:")
print('   git add "frontend/src/store/profileStore.ts"')
print('   git commit -m "fix(profile): 404 also invalidates cache"')
print("   git push origin main")