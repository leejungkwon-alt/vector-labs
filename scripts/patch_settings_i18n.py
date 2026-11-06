# scripts/patch_settings_i18n.py
from pathlib import Path
import sys

TARGET = Path("frontend/app/(tabs)/settings.tsx")
APPLY = "--apply" in sys.argv

if not TARGET.exists():
    print(f"❌ 파일을 찾을 수 없습니다: {TARGET}")
    sys.exit(1)

original = TARGET.read_text(encoding="utf-8")
txt = original

# 리스트(튜플)로 변경하여 치환 순서를 보장 (긴 문자열 먼저)
REPLACEMENTS = [
    ("SNS 계정 연동하기", 't("settings.linkAccountCta")'),
    ("계정 연동하기", 't("settings.linkAccountTitle")'),
    ("기기를 변경하거나 앱을 삭제해도 내 사주 데이터와 결제 정보를 안전하게 보관하려면 SNS 계정을 연동하세요.", 't("settings.linkAccountDesc")'),
    ("계정이 성공적으로 연결되었습니다.", 't("settings.linkAccountSuccess")'),
    ("알림", 't("common.notice")'),
]

for old, new in REPLACEMENTS:
    if old in txt:
        txt = txt.replace(old, new)
        print(f"✅ 교체: '{old[:15]}...' → '{new}'")

if txt == original:
    print("ℹ️ 교체할 하드코딩 텍스트를 찾지 못했습니다.")
    sys.exit(0)

if not APPLY:
    print("\n🧪 미리보기 모드입니다. 실제로 적용하려면 --apply 플래그를 추가하세요.")
    sys.exit(0)

TARGET.write_text(txt, encoding="utf-8")
print(f"\n🎉 패치 완료: {TARGET}")
print("   ⚠️ i18n JSON 파일(frontend/src/i18n/...)에 위 키들을 수동으로 추가해야 합니다.")