# scripts/patch_ui_fixes.py
"""
Gyeol 프론트엔드 UI/UX 패치 스크립트
- 사용법:
    python scripts/patch_ui_fixes.py           # 분석만 (안전)
    python scripts/patch_ui_fixes.py --apply   # 실제 패치 (백업 생성)
"""
from pathlib import Path
import re
import sys
import shutil
from datetime import datetime

# ---------- 1. 프로젝트 루트 / 검색 경로 결정 ----------
ROOT = Path(__file__).resolve().parent.parent
if (ROOT / "frontend").exists():
    SEARCH_ROOT = ROOT / "frontend"
else:
    SEARCH_ROOT = ROOT

print(f"🔎 검색 루트: {SEARCH_ROOT}")
print(f"🔎 전체 프로젝트 루트: {ROOT}\n")

# ---------- 2. settings 관련 .tsx 파일 자동 탐색 ----------
def find_settings_files():
    hits = []
    for pat in ["app/settings.tsx", "**/settings.tsx",
                "**/Settings*.tsx", "**/settings*.tsx"]:
        hits.extend(SEARCH_ROOT.glob(pat))
    # 중복 제거
    uniq = []
    for f in hits:
        if f.is_file() and f not in uniq:
            uniq.append(f)
    return uniq

settings_files = find_settings_files()

if not settings_files:
    print("❌ settings 관련 .tsx 파일을 찾지 못했습니다.")
    print("\n📂 프로젝트에서 발견된 .tsx 파일 목록 (최대 50개):")
    count = 0
    for f in SEARCH_ROOT.rglob("*.tsx"):
        print(f"   - {f.relative_to(ROOT)}")
        count += 1
        if count >= 50:
            print("   ... (이하 생략)")
            break
    print("\n👉 위 목록을 저에게 붙여주시면 정확한 경로로 패치 스크립트를 다시 만들어 드립니다.")
    sys.exit(1)

print("✅ settings 후보 파일:")
for f in settings_files:
    print(f"   - {f.relative_to(ROOT)}")

# ---------- 3. 문제 코드 스캔 ----------
print("\n🩺 문제 코드 스캔 (billing/history, paymentHistory, 404 의심):")
problem_files = []
for f in SEARCH_ROOT.rglob("*.tsx"):
    try:
        txt = f.read_text(encoding="utf-8")
    except Exception:
        continue
    reasons = []
    if "/billing/history" in txt or "billing/history" in txt:
        reasons.append("billing/history 호출")
    if "paymentHistory" in txt or "PaymentHistory" in txt:
        reasons.append("paymentHistory 상태/렌더")
    if "결제 내역" in txt:
        reasons.append("'결제 내역' 텍스트")
    if reasons:
        print(f"   ⚠️ {f.relative_to(ROOT)}  →  {', '.join(reasons)}")
        problem_files.append(f)

if not problem_files:
    print("   ✅ 문제 코드가 발견되지 않았습니다. (이미 정리되었을 수 있음)")

# ---------- 4. 패치 실행 여부 확인 ----------
APPLY = "--apply" in sys.argv
if not APPLY:
    print("\n🧪 지금은 '분석 모드' 입니다. 실제 파일은 변경되지 않았습니다.")
    print("   실제로 패치하려면:  python scripts/patch_ui_fixes.py --apply")
    sys.exit(0)

if not problem_files:
    print("\n✅ 패치할 대상이 없습니다. 종료.")
    sys.exit(0)

# ---------- 5. 백업 폴더 생성 ----------
backup_dir = ROOT / "scripts" / "_backups"
backup_dir.mkdir(exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# ---------- 6. 파일별 패치 ----------
PORTAL_BLOCK = """
      {/* Lemon Squeezy 고객 포털 버튼 */}
      <TouchableOpacity
        style={{ backgroundColor: "#007AFF", paddingVertical: 12,
                 paddingHorizontal: 24, borderRadius: 8, marginTop: 16,
                 alignItems: "center" }}
        onPress={() => Linking.openURL("https://gyeol.lemonsqueezy.com/billing")}
      >
        <Text style={{ color: "#FFFFFF", fontSize: 16, fontWeight: "600" }}>
          구독 및 결제 관리
        </Text>
      </TouchableOpacity>
"""

def ensure_linking_import(txt: str) -> str:
    if "Linking" in txt and re.search(r"from\s+['\"]react-native['\"]", txt):
        # 이미 Linking import 되어있으면 그대로
        m = re.search(r"import\s*\{([^}]*)\}\s*from\s*['\"]react-native['\"]", txt)
        if m and "Linking" in m.group(1):
            return txt
        if m:
            # 기존 import 구문에 Linking 추가
            names = [n.strip() for n in m.group(1).split(",") if n.strip()]
            names.append("Linking")
            new_import = "import { " + ", ".join(sorted(set(names))) + " } from 'react-native'"
            return txt[:m.start()] + new_import + txt[m.end():]
    return txt

for f in problem_files:
    txt = f.read_text(encoding="utf-8")
    original = txt

    # (a) billing/history 호출 라인 제거 (한 줄 또는 블록)
    txt = re.sub(r"\s*(?:await\s+)?(?:fetch|axios\.get|api\.get)\(\s*['\"][^'\"]*billing/history['\"][^;]*;?", "", txt)

    # (b) paymentHistory 상태 선언 제거
    txt = re.sub(r"const\s*\[\s*paymentHistory\s*,\s*setPaymentHistory\s*\]\s*=\s*useState[^;]*;", "", txt)

    # (c) paymentHistory 렌더링 블록 제거 (대략적인 map 블록)
    txt = re.sub(r"\{[^{}]*paymentHistory\.map\([^{}]*\{.*?\}[^{}]*\)\}", "", txt, flags=re.DOTALL)

    # (d) 고객 포털 버튼 삽입 (프리미엄 조건부 렌더링 근처)
    if "구독 및 결제 관리" not in txt:
        # '프리미엄' 텍스트 직후 삽입 시도
        if "프리미엄" in txt:
            # JSX 안전하게 삽입하기 위해 첫 등장 위치 다음에 추가
            idx = txt.find("프리미엄")
            # 그 다음 닫는 태그 뒤에 삽입
            close_idx = txt.find(">", idx)
            if close_idx != -1:
                txt = txt[:close_idx+1] + PORTAL_BLOCK + txt[close_idx+1:]

    # (e) Linking import 보장
    txt = ensure_linking_import(txt)

    if txt != original:
        bak = backup_dir / f"{f.name}.{stamp}.bak"
        shutil.copy2(f, bak)
        f.write_text(txt, encoding="utf-8")
        print(f"   ✅ 패치 완료: {f.relative_to(ROOT)}  (백업: {bak.relative_to(ROOT)})")
    else:
        print(f"   ⏭️  변경 없음: {f.relative_to(ROOT)}")

print("\n🎉 패치 작업 종료.")
print("   다음 단계:  cd frontend && npx expo export --platform web  →  Vercel 재배포")