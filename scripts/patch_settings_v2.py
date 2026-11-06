# scripts/patch_settings_v2.py
"""
Gyeol settings.tsx 정밀 패치 v2
- 사용법:
    python scripts/patch_settings_v2.py            # 미리보기 (dry-run)
    python scripts/patch_settings_v2.py --apply    # 실제 적용 (자동 백업)
"""
from pathlib import Path
import shutil
from datetime import datetime
import sys

TARGET = Path("frontend/app/(tabs)/settings.tsx")
APPLY = "--apply" in sys.argv

if not TARGET.exists():
    print(f"❌ 대상 파일 없음: {TARGET}")
    sys.exit(1)

original = TARGET.read_text(encoding="utf-8")
txt = original

# -------------------------------------------------------------------
# 1) useQuery import 제거 (더 이상 사용 안 함)
# -------------------------------------------------------------------
REPLACEMENTS = [
    (
        'import { useQuery } from "@tanstack/react-query";\n',
        '',
        "useQuery import 제거",
    ),
    # ---------------------------------------------------------------
    # 2) api.getPurchases() 호출 제거 → 404의 근본 원인
    # ---------------------------------------------------------------
    (
        '''  const { data: purchaseData } = useQuery({
    queryKey: ["purchases", user?.id],
    queryFn: () => api.getPurchases(),
    enabled: !!user,
  });

''',
        '',
        "getPurchases useQuery 호출 제거 (404 원인)",
    ),
    # ---------------------------------------------------------------
    # 3) 구독 관리 링크를 Lemon Squeezy 고객 포털로 교체
    # ---------------------------------------------------------------
    (
        '''  const handleManageSubscription = () => {
    if (Platform.OS === "ios") {
      Linking.openURL("https://apps.apple.com/account/subscriptions");
    } else if (Platform.OS === "android") {
      Linking.openURL("https://play.google.com/store/account/subscriptions");
    } else {
      alert(t("settings.manageSubscriptionWeb"));
    }
  };''',
        '''  const handleManageSubscription = () => {
    // Lemon Squeezy 고객 포털 (구독 관리·카드 변경·영수증 다운로드)
    // TODO: 백엔드에서 signed URL을 받아 자동 로그인으로 전환 예정
    Linking.openURL("https://gyeol.lemonsqueezy.com/billing");
  };''',
        "handleManageSubscription → Lemon Squeezy 포털 링크로 교체",
    ),
]

for old, new, label in REPLACEMENTS:
    cnt = txt.count(old)
    if cnt != 1:
        print(f"❌ [{label}] 정확히 1회 등장해야 하는데 {cnt}회 발견. 중단.")
        print("   --- 찾는 문자열 미리보기 ---")
        print(repr(old[:120]))
        sys.exit(1)
    txt = txt.replace(old, new, 1)
    print(f"✅ [{label}]")

# -------------------------------------------------------------------
# 4) "결제 내역 (영수증)" 섹션 통째로 제거
#    시작 마커: {/* 3.5 결제 내역 (영수증) */}
#    종료 마커: {/* 4. 계정 액션 */}
# -------------------------------------------------------------------
START_MARK = '      {/* 3.5 결제 내역 (영수증) */}'
END_MARK = '      {/* 4. 계정 액션 */}'
s = txt.find(START_MARK)
e = txt.find(END_MARK)
if s == -1 or e == -1 or s >= e:
    print("❌ 결제 내역 섹션 마커를 정확히 찾지 못했습니다. 중단.")
    print(f"   START_MARK 발견: {s != -1}, END_MARK 발견: {e != -1}")
    sys.exit(1)
removed = txt[s:e]
txt = txt[:s] + txt[e:]
print(f"✅ [결제 내역 섹션 제거] {len(removed.splitlines())}줄 삭제")

# -------------------------------------------------------------------
# 5) 잔여 참조 검사 (하나라도 있으면 실패)
# -------------------------------------------------------------------
LEFTOVER = [
    "purchaseData",
    "api.getPurchases",
    "sub_monthly_299",
    "addon_compat_199",
    "addon_deep_099",
    "apps.apple.com/account/subscriptions",
    "play.google.com/store/account/subscriptions",
]
problems = [p for p in LEFTOVER if p in txt]
if problems:
    print(f"❌ 잔여 참조 발견, 중단: {problems}")
    sys.exit(1)
print("✅ [잔여 참조 검사] 통과")

# -------------------------------------------------------------------
# 6) 괄호 균형 sanity check
# -------------------------------------------------------------------
def delta(s, ch):
    return s.count(ch[0]) - s.count(ch[1])

for pair in ["()", "{}", "[]"]:
    if delta(original, pair) != delta(txt, pair):
        print(f"❌ 괄호 균형이 변했습니다: {pair}. 중단.")
        sys.exit(1)
print("✅ [괄호 균형 검사] 통과")

# -------------------------------------------------------------------
# 7) 적용 or 미리보기
# -------------------------------------------------------------------
print(f"\n📏 라인 수: {len(original.splitlines())} → {len(txt.splitlines())}")

if not APPLY:
    print("\n🧪 미리보기 모드입니다. 파일은 변경되지 않았습니다.")
    print("   실제로 적용하려면:  python scripts/patch_settings_v2.py --apply")
    sys.exit(0)

backup_dir = Path("scripts/_backups")
backup_dir.mkdir(parents=True, exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
bak = backup_dir / f"settings.tsx.{stamp}.bak"
shutil.copy2(TARGET, bak)

TARGET.write_text(txt, encoding="utf-8")
print(f"\n🎉 패치 완료: {TARGET}")
print(f"   백업: {bak}")
print("\n👉 다음 단계:")
print("   1) cd frontend")
print("   2) 프론트 개발 서버 재시작 (npx expo start --web)")
print("   3) 브라우저 개발자도구 Network 탭에서 404 사라졌는지 확인")
print("   4) 이상 없으면 git diff로 최종 리뷰 후 Vercel 재배포")