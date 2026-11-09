# scripts/patch_login_modal_default.py
from pathlib import Path
import sys
import difflib

PATH = Path("frontend/src/components/SocialLoginModal.tsx")

if not PATH.exists():
    print(f"❌ 파일 없음: {PATH}")
    sys.exit(1)

src = PATH.read_text(encoding="utf-8")

old_str = 'const [mode, setMode] = useState<"link" | "login">("link");'
new_str = 'const [mode, setMode] = useState<"link" | "login">("login");'

if new_str in src:
    print("⚠️ 이미 'login'이 기본값으로 설정되어 있습니다.")
    sys.exit(0)

if old_str not in src:
    print("❌ 대상 코드를 찾을 수 없습니다. 수동 확인 필요.")
    sys.exit(1)

patched = src.replace(old_str, new_str, 1)

print("===== DIFF PREVIEW =====")
sys.stdout.writelines(
    difflib.unified_diff(
        src.splitlines(keepends=True),
        patched.splitlines(keepends=True),
        fromfile="before",
        tofile="after",
        n=2,
    )
)

if "--apply" not in sys.argv:
    print("\n💡 dry-run입니다. 실제 적용: python scripts/patch_login_modal_default.py --apply")
    sys.exit(0)

PATH.write_text(patched, encoding="utf-8")
print("\n✅ 패치 완료!")