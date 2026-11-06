# scripts/patch_all_i18n.py
import json
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

# 언어별 추가할 번역 데이터
TRANSLATIONS = {
    "ko": {
        "linkAccountTitle": "계정 연동하기",
        "linkAccountDesc": "기기를 변경하거나 앱을 삭제해도 내 사주 데이터와 결제 정보를 안전하게 보관하려면 SNS 계정을 연동하세요.",
        "linkAccountCta": "SNS 계정 연동하기",
        "linkAccountSuccess": "계정이 성공적으로 연결되었습니다.",
    },
    "en": {
        "linkAccountTitle": "Link Account",
        "linkAccountDesc": "Link your social account to safely keep your saju data and payment info even if you change devices or delete the app.",
        "linkAccountCta": "Link Social Account",
        "linkAccountSuccess": "Account successfully linked.",
    },
    "ja": {
        "linkAccountTitle": "アカウント連携",
        "linkAccountDesc": "機種変更やアプリ削除時でも、四柱推命データと決済情報を安全に保つためにSNSアカウントを連携してください。",
        "linkAccountCta": "SNSアカウントを連携",
        "linkAccountSuccess": "アカウントが正常に連携されました。",
    },
    "zh": {
        "linkAccountTitle": "关联账号",
        "linkAccountDesc": "即使更换设备或删除应用，为了安全保存您的四柱数据和支付信息，请关联SNS账号。",
        "linkAccountCta": "关联SNS账号",
        "linkAccountSuccess": "账号关联成功。",
    },
    "es": {
        "linkAccountTitle": "Vincular cuenta",
        "linkAccountDesc": "Vincule su cuenta de redes sociales para mantener seguros sus datos de saju e información de pago incluso si cambia de dispositivo o elimina la aplicación.",
        "linkAccountCta": "Vincular cuenta social",
        "linkAccountSuccess": "Cuenta vinculada con éxito.",
    }
}

def get_lang_key(filename):
    """파일명에서 언어 키 추출 (예: ko.json -> ko, zh-CN.json -> zh)"""
    stem = filename.stem.lower()
    if stem.startswith("zh"): return "zh"
    if stem.startswith("ja"): return "ja"
    if stem.startswith("es"): return "es"
    if stem.startswith("ko"): return "ko"
    if stem.startswith("en"): return "en"
    return None

# frontend 폴더 내의 모든 .json 파일 탐색 (node_modules 제외)
json_files = [p for p in Path("frontend").rglob("*.json") if "node_modules" not in str(p)]
target_files = []

for f in json_files:
    lang = get_lang_key(f)
    if lang and lang in TRANSLATIONS:
        target_files.append((f, lang))

if not target_files:
    print("❌ 번역 JSON 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
    sys.exit(1)

print(f"🔎 발견된 번역 파일 {len(target_files)}개")

for f, lang in target_files:
    try:
        with open(f, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception:
        continue

    if not isinstance(data, dict):
        continue

    changed = False

    # 1. common.notice 추가
    if "common" not in data:
        data["common"] = {}
    if "notice" not in data["common"]:
        data["common"]["notice"] = "알림" if lang == "ko" else ("Notice" if lang == "en" else "Notice")
        changed = True

    # 2. settings 키 추가
    if "settings" not in data:
        data["settings"] = {}
    
    for key, value in TRANSLATIONS[lang].items():
        if key not in data["settings"]:
            data["settings"][key] = value
            changed = True

    if changed:
        if APPLY:
            with open(f, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            print(f"🎉 {f} 패치 완료")
        else:
            print(f"🧪 {f} 패치 예정 (미리보기)")

if not APPLY:
    print("\n🧪 미리보기 모드입니다. 실제로 적용하려면 --apply 플래그를 추가하세요.")
    print("   python scripts/patch_all_i18n.py --apply")