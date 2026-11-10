# scripts/patch_i18n_telegram.py
import json
from pathlib import Path
import sys

KEYS = {
    "ko": {
        "telegramPushTitle": "텔레그램 데일리 운세",
        "telegramPushDesc": "매일 아침 텔레그램으로 오늘의 운세를 받아보세요.",
        "telegramPushCta": "구독하기",
        "telegramPushSuccess": "데일리 푸시 알림이 구독되었습니다!",
        "telegramPushNoProfile": "출생 정보를 먼저 저장해 주세요.",
        "telegramPushAgeLimit": "만 14세 미만은 이용할 수 없습니다.",
        "telegramPushError": "구독에 실패했습니다. 다시 시도해 주세요."
    },
    "en": {
        "telegramPushTitle": "Telegram Daily Fortune",
        "telegramPushDesc": "Get your daily fortune on Telegram every morning.",
        "telegramPushCta": "Subscribe",
        "telegramPushSuccess": "Daily push notifications subscribed!",
        "telegramPushNoProfile": "Please save your birth profile first.",
        "telegramPushAgeLimit": "You must be at least 14 years old.",
        "telegramPushError": "Subscription failed. Please try again."
    },
    "ja": {
        "telegramPushTitle": "Telegram 毎日の運勢",
        "telegramPushDesc": "毎朝、Telegramで今日の運勢を受け取れます。",
        "telegramPushCta": "購読する",
        "telegramPushSuccess": "毎日のプッシュ通知を購読しました！",
        "telegramPushNoProfile": "先に出生情報を保存してください。",
        "telegramPushAgeLimit": "14歳未満はご利用いただけません。",
        "telegramPushError": "購読に失敗しました。もう一度お試しください。"
    },
    "zh_cn": {
        "telegramPushTitle": "Telegram 每日运势",
        "telegramPushDesc": "每天早上在Telegram接收今日运势。",
        "telegramPushCta": "订阅",
        "telegramPushSuccess": "已成功订阅每日推送！",
        "telegramPushNoProfile": "请先保存出生信息。",
        "telegramPushAgeLimit": "未满14岁无法使用。",
        "telegramPushError": "订阅失败，请重试。"
    },
    "es": {
        "telegramPushTitle": "Fortuna Diaria en Telegram",
        "telegramPushDesc": "Recibe tu fortuna diaria en Telegram cada mañana.",
        "telegramPushCta": "Suscribirse",
        "telegramPushSuccess": "¡Notificaciones diarias suscritas!",
        "telegramPushNoProfile": "Por favor, guarda tu perfil de nacimiento primero.",
        "telegramPushAgeLimit": "Debes tener al menos 14 años.",
        "telegramPushError": "Suscripción fallida. Por favor, inténtalo de nuevo."
    }
}

for lang, data in KEYS.items():
    path = Path(f"frontend/src/locales/{lang}.json")
    if not path.exists(): continue
    with path.open(encoding="utf-8") as f:
        content = json.load(f)
    if "settings" not in content: content["settings"] = {}
    for k, v in data.items():
        content["settings"][k] = v
    with path.open("w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"✅ {lang}.json settings 텔레그램 키 추가됨")