# scripts/patch_social_login_i18n.py
import json
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
TARGET = Path("frontend/src/components/SocialLoginModal.tsx")

if not TARGET.exists():
    print(f"❌ 파일을 찾을 수 없습니다: {TARGET}")
    sys.exit(1)

# ---------------- [1] TSX 파일 패치 ----------------
original = TARGET.read_text(encoding="utf-8")
txt = original

# 1) useT 훅 import 추가
if "useT" not in txt:
    txt = txt.replace('import { useAuthStore } from "@/store/authStore";', 'import { useAuthStore } from "@/store/authStore";\nimport { useT } from "@/i18n";')

# 2) 컴포넌트 내부에 t 훅 선언
if "const t = useT();" not in txt:
    txt = txt.replace('  const linkAccount = useAuthStore((s) => s.linkAccount);', '  const linkAccount = useAuthStore((s) => s.linkAccount);\n  const t = useT();')

# 3) 하드코딩된 텍스트 교체 (정규식 사용)
replacements = [
    (r'window\.alert\(e\.message \|\| "로그인에 실패했습니다\."\);', 'window.alert(e.message || t("socialLogin.loginFailed"));'),
    (r'Alert\.alert\(\'알림\', e\.message \|\| "로그인에 실패했습니다\."\);', 'Alert.alert(t("common.notice"), e.message || t("socialLogin.loginFailed"));'),
    (r'>계정 연결</Text>', '>{t("socialLogin.title")}</Text>'),
    (r'기기를 변경하거나 앱을 삭제해도\{"\\n"\}내 사주 데이터와 결제 정보를 안전하게 보관합니다\.', '{t("socialLogin.desc")}'),
    (r'>Apple로 계속하기</Text>', '>{t("socialLogin.appleCta")}</Text>'),
    (r'>Google로 계속하기</Text>', '>{t("socialLogin.googleCta")}</Text>'),
    (r'>카카오로 계속하기</Text>', '>{t("socialLogin.kakaoCta")}</Text>'),
    (r'>나중에 하기</Text>', '>{t("socialLogin.later")}</Text>'),
]

for pattern, repl in replacements:
    if re.search(pattern, txt):
        txt = re.sub(pattern, repl, txt)
    else:
        # 만약 정규식 매칭이 실패하면 단순 문자열 교체 시도 (줄바꿈 등 예외처리)
        if "Apple로 계속하기" in txt: txt = txt.replace("Apple로 계속하기", "{t(\"socialLogin.appleCta\")}")
        if "Google로 계속하기" in txt: txt = txt.replace("Google로 계속하기", "{t(\"socialLogin.googleCta\")}")
        if "카카오로 계속하기" in txt: txt = txt.replace("카카오로 계속하기", "{t(\"socialLogin.kakaoCta\")}")
        if "나중에 하기" in txt: txt = txt.replace("나중에 하기", "{t(\"socialLogin.later\")}")
        if "계정 연결" in txt: txt = txt.replace("계정 연결", "{t(\"socialLogin.title\")}")
        if "기기를 변경하거나 앱을 삭제해도" in txt: txt = txt.replace("기기를 변경하거나 앱을 삭제해도{\"\\n\"}내 사주 데이터와 결제 정보를 안전하게 보관합니다.", "{t(\"socialLogin.desc\")}")


# ---------------- [2] JSON 번역 파일 패치 ----------------
TRANSLATIONS = {
    "ko": {
        "loginFailed": "로그인에 실패했습니다.",
        "title": "계정 연결",
        "desc": "기기를 변경하거나 앱을 삭제해도\\n내 사주 데이터와 결제 정보를 안전하게 보관합니다.",
        "appleCta": "Apple로 계속하기",
        "googleCta": "Google로 계속하기",
        "kakaoCta": "카카오로 계속하기",
        "later": "나중에 하기"
    },
    "en": {
        "loginFailed": "Login failed.",
        "title": "Link Account",
        "desc": "Keep your saju data and payment info safe\\neven if you change devices or delete the app.",
        "appleCta": "Continue with Apple",
        "googleCta": "Continue with Google",
        "kakaoCta": "Continue with Kakao",
        "later": "Later"
    },
    "ja": {
        "loginFailed": "ログインに失敗しました。",
        "title": "アカウント連携",
        "desc": "機種変更やアプリ削除時でも\\n四柱推命データと決済情報を安全に保管します。",
        "appleCta": "Appleで続ける",
        "googleCta": "Googleで続ける",
        "kakaoCta": "Kakaoで続ける",
        "later": "後で"
    },
    "zh": {
        "loginFailed": "登录失败。",
        "title": "关联账号",
        "desc": "即使更换设备或删除应用，\\n也能安全保存您的四柱数据和支付信息。",
        "appleCta": "使用 Apple 继续",
        "googleCta": "使用 Google 继续",
        "kakaoCta": "使用 Kakao 继续",
        "later": "稍后"
    },
    "es": {
        "loginFailed": "Error al iniciar sesión.",
        "title": "Vincular cuenta",
        "desc": "Mantenga seguros sus datos de saju e información de pago\\nincluso si cambia de dispositivo o elimina la aplicación.",
        "appleCta": "Continuar con Apple",
        "googleCta": "Continuar con Google",
        "kakaoCta": "Continuar con Kakao",
        "later": "Más tarde"
    }
}

def get_lang_key(filename):
    stem = filename.stem.lower()
    if stem.startswith("zh"): return "zh"
    if stem.startswith("ja"): return "ja"
    if stem.startswith("es"): return "es"
    if stem.startswith("ko"): return "ko"
    if stem.startswith("en"): return "en"
    return None

json_files = [p for p in Path("frontend").rglob("*.json") if "node_modules" not in str(p) and get_lang_key(p)]

# ---------------- [3] 실행 및 저장 ----------------
if not APPLY:
    print("🧪 미리보기 모드입니다. 실제로 적용하려면 --apply 플래그를 추가하세요.")
    if txt != original:
        print(f"  - {TARGET} 수정 예정")
    for f in json_files:
        print(f"  - {f} 업데이트 예정")
    sys.exit(0)

# TSX 저장
if txt != original:
    TARGET.write_text(txt, encoding="utf-8")
    print(f"🎉 TSX 패치 완료: {TARGET}")

# JSON 저장
for f in json_files:
    lang = get_lang_key(f)
    if lang not in TRANSLATIONS:
        continue
    try:
        with open(f, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception:
        continue

    if not isinstance(data, dict):
        continue

    if "socialLogin" not in data:
        data["socialLogin"] = {}
    
    changed = False
    for key, value in TRANSLATIONS[lang].items():
        if key not in data["socialLogin"]:
            data["socialLogin"][key] = value
            changed = True

    if changed:
        with open(f, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        print(f"🎉 JSON 패치 완료: {f}")

print("\n✅ 모든 패치가 완료되었습니다.")