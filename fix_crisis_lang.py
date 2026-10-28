from pathlib import Path

# 1. crisis_resources.py 다국어 완벽 지원 버전으로 교체
crisis_code = '''"""
위기 신호 대응 — 지역별 자살예방/응급 리소스.
다국어(lang) 지원 버전.
"""

_CRISIS_DATA = {
    "KOREA": {
        "phone": "109",
        "url": "https://www.suicide.or.kr",
        "hotline": {
            "ko": "자살예방상담전화",
            "en": "Korea Suicide Prevention Hotline",
            "ja": "韓国自殺予防ホットライン",
            "zh_cn": "韩国自杀预防热线",
            "es": "Línea de Prevención del Suicidio de Corea",
        },
        "note": {
            "ko": "24시간 무료 상담",
            "en": "24-hour free counseling",
            "ja": "24時間無料相談",
            "zh_cn": "24小时免费咨询",
            "es": "Asesoramiento gratuito 24 horas",
        },
    },
    "JAPAN": {
        "phone": "0120-783-556",
        "url": "https://www.inochinodenwa.org",
        "hotline": {
            "ko": "일본 생명의 전화",
            "en": "Inochi no Denwa (Japan)",
            "ja": "いのちの電話",
            "zh_cn": "日本生命电话",
            "es": "Línea de Vida de Japón",
        },
        "note": {
            "ko": "24시간 대응",
            "en": "24-hour support",
            "ja": "24時間対応",
            "zh_cn": "24小时对应",
            "es": "Atención 24 horas",
        },
    },
    "NORTH_AMERICA": {
        "phone": "988",
        "url": "https://988lifeline.org",
        "text": "Text HOME to 741741",
        "hotline": {
            "ko": "988 자살 및 위기 상담 라인",
            "en": "988 Suicide & Crisis Lifeline",
            "ja": "988 自殺・危機ライフライン",
            "zh_cn": "988 自杀与危机生命线",
            "es": "Línea de Prevención del Suicidio y Crisis 988",
        },
        "note": {
            "ko": "미국/캐나다. 다른 지역은 URL 참조.",
            "en": "US/Canada. For other regions, see url.",
            "ja": "米国/カナダ。その他の地域はURLを参照。",
            "zh_cn": "美国/加拿大。其他地区请参考网址。",
            "es": "EE. UU./Canadá. Para otras regiones, consulte la URL.",
        },
    },
    "EUROPE": {
        "phone": "116 123",
        "url": "https://www.samaritans.org",
        "hotline": {
            "ko": "사마리안즈 (영국/아일랜드)",
            "en": "Samaritans (UK/ROI)",
            "ja": "サマリタンズ (英/アイルランド)",
            "zh_cn": "撒玛利亚会 (英国/爱尔兰)",
            "es": "Samaritans (Reino Unido/Irlanda)",
        },
        "note": {
            "ko": "영국/아일랜드 무료 전화. 유럽연합(EU)은 URL 참조.",
            "en": "Free from any phone in UK/ROI. EU: see url for local lines.",
            "ja": "英/アイルランドで無料。EUはURL参照。",
            "zh_cn": "英国/爱尔兰免费。欧盟请参考网址。",
            "es": "Gratis en Reino Unido/Irlanda. UE: consulte la URL.",
        },
    },
    "OCEANIA": {
        "phone": "13 11 14",
        "url": "https://www.lifeline.org.au",
        "hotline": {
            "ko": "라이프라인 (호주)",
            "en": "Lifeline (Australia)",
            "ja": "ライフライン (オーストラリア)",
            "zh_cn": "生命线 (澳大利亚)",
            "es": "Lifeline (Australia)",
        },
        "note": {
            "ko": "호주 24시간. 뉴질랜드: 1737.",
            "en": "24/7 in Australia. NZ: 1737.",
            "ja": "オーストラリア 24/7。NZ: 1737。",
            "zh_cn": "澳大利亚24小时。新西兰：1737。",
            "es": "24/7 en Australia. NZ: 1737.",
        },
    },
    "GREATER_CHINA": {
        "phone": "800-810-1117 / 010-8295-1332",
        "url": "https://www.crisis.org.cn",
        "hotline": {
            "ko": "베이징 자살연구 및 예방센터",
            "en": "Beijing Suicide Research and Prevention Center",
            "ja": "北京自殺研究予防センター",
            "zh_cn": "北京心理危机研究与干预中心",
            "es": "Centro de Investigación y Prevención del Suicidio de Pekín",
        },
        "note": {
            "ko": "중국 본토. 홍콩: 2382 0000. 대만: 1925.",
            "en": "Mainland China. HK: 2382 0000. TW: 1925.",
            "ja": "中国本土。香港: 2382 0000。台湾: 1925。",
            "zh_cn": "中国大陆。香港：2382 0000。台湾：1925。",
            "es": "China continental. HK: 2382 0000. TW: 1925.",
        },
    },
    "SOUTHEAST_ASIA": {
        "phone": "1-767",
        "url": "https://www.sos.org.sg",
        "hotline": {
            "ko": "SOS (싱가포르)",
            "en": "SOS (Singapore)",
            "ja": "SOS (シンガポール)",
            "zh_cn": "SOS (新加坡)",
            "es": "SOS (Singapur)",
        },
        "note": {
            "ko": "싱가포르 24시간. 다른 국가는 URL 참조.",
            "en": "Singapore 24h. Other countries: see url.",
            "ja": "シンガポール 24時間。その他はURL参照。",
            "zh_cn": "新加坡24小时。其他国家请参考网址。",
            "es": "Singapur 24h. Otros países: consulte la URL.",
        },
    },
}

_GLOBAL_FALLBACK_DATA = {
    "phone": "",
    "url": "https://findahelpline.com/",
    "hotline": {
        "ko": "지역별 핫라인 찾기",
        "en": "Find a helpline",
        "ja": "地域のホットラインを探す",
        "zh_cn": "查找当地热线",
        "es": "Buscar una línea de ayuda",
    },
    "note": {
        "ko": "즉각적인 위험에 처해 있다면 지역 응급 번호로 전화하세요.",
        "en": "If you are in immediate danger, call your local emergency number.",
        "ja": "差し迫った危険がある場合は、地域の緊急番号に電話してください。",
        "zh_cn": "如果您处于紧急危险中，请拨打当地的紧急号码。",
        "es": "Si está en peligro inmediato, llame a su número de emergencia local.",
    },
}


def _pick(data: dict, lang: str, default_lang: str = "en") -> str:
    val = data.get(lang, data.get(default_lang, ""))
    return val if isinstance(val, str) else ""


def get_crisis_resources(region: str | None = None, lang: str = "en") -> dict:
    """지역 리소스. 없으면 글로벌 fallback. 항상 dict 반환."""
    if region and region in _CRISIS_DATA:
        data = _CRISIS_DATA[region]
    else:
        data = _GLOBAL_FALLBACK_DATA

    result = {}
    for k, v in data.items():
        if isinstance(v, dict):
            result[k] = _pick(v, lang)
        else:
            result[k] = v
    return result


def list_regions() -> list:
    return sorted(_CRISIS_DATA.keys())
'''

path_crisis = Path("app/compliance/crisis_resources.py")
path_crisis.write_text(crisis_code, encoding="utf-8")
print("✅ app/compliance/crisis_resources.py 다국어 패치 완료")

# 2. content_writer.py 호출부 수정 (lang 파라미터 전달)
path_cw = Path("app/services/content_writer.py")
cw_text = path_cw.read_text(encoding="utf-8")
if 'get_crisis_resources(profile.get("region"), lang)' not in cw_text:
    cw_text = cw_text.replace(
        'get_crisis_resources(profile.get("region"))',
        'get_crisis_resources(profile.get("region"), lang)'
    )
    path_cw.write_text(cw_text, encoding="utf-8")
    print("✅ app/services/content_writer.py 패치 완료")
else:
    print("✔️ content_writer.py 이미 패치됨")
    