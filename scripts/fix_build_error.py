# scripts/fix_build_error.py
from pathlib import Path
import sys

TARGET = Path("frontend/app/(tabs)/settings.tsx")
APPLY = "--apply" in sys.argv

if not TARGET.exists():
    print(f"❌ 파일을 찾을 수 없습니다: {TARGET}")
    sys.exit(1)

original = TARGET.read_text(encoding="utf-8")
txt = original

# 1. 자바스크립트 문자열 따옴표 중첩 오류 수정
txt = txt.replace('const msg = "t("settings.linkAccountSuccess")";', 'const msg = t("settings.linkAccountSuccess");')
txt = txt.replace('else Alert.alert("t("common.notice")", msg);', 'else Alert.alert(t("common.notice"), msg);')

# 2. 주석 오염 복구
txt = txt.replace('// 단순히 계정 연동 버튼을 눌러서 들어온 경우 -> 성공 t("common.notice")만 띄우고 종료', '// 단순히 계정 연동 버튼을 눌러서 들어온 경우 -> 성공 알림만 띄우고 종료')

# 3. JSX 텍스트 내 t() 함수에 중괄호 {} 누락된 부분 수정
txt = txt.replace('>t("settings.linkAccountTitle")</Text>', '>{t("settings.linkAccountTitle")}</Text>')
txt = txt.replace('            t("settings.linkAccountDesc")\n', '            {t("settings.linkAccountDesc")}\n')
txt = txt.replace('>t("settings.linkAccountCta")</Text>', '>{t("settings.linkAccountCta")}</Text>')

if txt == original:
    print("ℹ️ 수정할 오류 코드를 찾지 못했습니다. 이미 수정되었을 수 있습니다.")
    sys.exit(0)

if not APPLY:
    print("🧪 미리보기 모드입니다. 실제로 적용하려면 --apply 플래그를 추가하세요.")
    sys.exit(0)

TARGET.write_text(txt, encoding="utf-8")
print(f"🎉 빌드 에러 수정 완료: {TARGET}")
print("   이제 git commit & push 하시면 Vercel 빌드가 성공합니다.")