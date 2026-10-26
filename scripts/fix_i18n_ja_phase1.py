#!/usr/bin/env python3
"""
Phase 1 (JA): 기반 팩 번역.

- errors.json  : DST 에러 메시지 (전면)
- labels.json  : UI 라벨 전체 (SINSAL/CHART/PERSONALIZATION)
- sections.json: 메타데이터 + DISCLAIMER 만 (MONEY/WORK/BONDS는 Phase 2)
- year.json    : DEFAULT_YEAR_THEME + SOLAR_CALENDAR_NOTE 만 (YEAR_THEME_CONTENT는 Phase 2)

설계: es Phase 3 와 동일한 copy-then-override. ja 파일은 이미 존재(백필 완료)하므로,
      존재하는 파일을 로드해 지정한 키만 덮어쓴다.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JA = ROOT / "app" / "services" / "content" / "data" / "ja"

files_written = []
skipped = []
failed = []


# ─────────────────────────────────────────────────────────
# 1. errors.json
# ─────────────────────────────────────────────────────────
ERRORS_JA = {
    "DST_AMBIGUOUS": (
        "この時刻は曖昧です：{clock} は {tz} で二回発生します。"
        "dst_fold=0（オフセット {off0}）または dst_fold=1（オフセット {off1}）"
        "で再リクエストしてください。"
    ),
    "DST_GAP": (
        "この時刻は存在しません：{clock} は {tz} の夏時間によりスキップされています。"
    ),
}


# ─────────────────────────────────────────────────────────
# 2. labels.json
# ─────────────────────────────────────────────────────────
LABELS_JA = {
    "BALANCE_LABEL": "バランス",
    "CHART_HERO": "あなたの設計図、4つの顔。",
    "CHART_LAYER_META": {
        "year_pillar": {"label": "幼少期",
                        "role": "あなたのルーツ — 始まりと家族の影響"},
        "month_pillar": {"label": "キャリア",
                         "role": "あなたの社会生活 — どう働き、どう関わるか"},
        "day_pillar": {"label": "核となる自分",
                       "role": "本当のアイデンティティ — 本質のあなた"},
        "hour_pillar": {"label": "未来",
                        "role": "あなたの内面世界 — 夢と晩年"},
    },
    "SINSAL_POS_LABEL": {
        "year_pillar": "ルーツ", "month_pillar": "キャリア",
        "day_pillar": "自分", "hour_pillar": "レガシー",
    },
    "SINSAL_POS_ROLE": {
        "year_pillar": "祖先 / 幼少期の環境",
        "month_pillar": "キャリア / 公の生活",
        "day_pillar": "自分 / パートナーシップ",
        "hour_pillar": "内面世界 / 遺産",
    },
    "SINSAL_THEME_KEYWORD": {
        "MAGNETIC_DRAW": "魅力と引き寄せ",
        "RESTLESS_FEET": "移動と探求",
        "SOLITARY_DEPTH": "内省と創造性",
        "ALLY_MAGNET": "助けと支援",
        "SCHOLAR_MIND": "学びと知識",
        "SHARP_EDGE": "推進と競争",
        "COMMANDER": "リーダーシップと決断",
    },
    "SINSAL_NOTE_TPL": (
        "この特性はあなたの{role}に位置し、その領域で{theme}の気が最も強く現れます。"
    ),
    "SINSAL_HERO_ONE": "あなたには1つの特別な気質があります。",
    "SINSAL_HERO_MANY": "あなたには{n}つの特別な気質があります。",
    "GRADE_LABELS": {
        "PEAK": "最高", "FAVORABLE": "追い風",
        "NEUTRAL": "中立", "CAUTION": "注意", "CHALLENGING": "試練",
    },
    "COMPAT_FALLBACK_HEADLINE": "関係は二人で一緒に築いていくものです。",
    "PERSONALIZATION_BLOCK": {
        "HEADER": "あなたの命式を深く読む、パーソナルインサイト",
        "BY_INTENSITY": {
            "SELF_SOURCED": (
                "あなたの強い「セルフソース」の気が、この傾向をより鮮明に、"
                "主体的に引き出します。"
            ),
            "ENVIRONMENT_TUNED": (
                "あなたの「環境反応型」の気質により、周りの環境や人との出会いに"
                "応じてこの傾向が深く現れます。"
            ),
            "BALANCED_CORE": (
                "あなたのバランスの取れた「中心」の気が、この傾向を安定して"
                "調和的に導きます。"
            ),
        },
        "BY_ELEMENT": {
            "GROWTH": "ここに成長（木）の気が加わり、絶えず拡張し新たな方向を開拓しようとする欲求が強く働きます。",
            "SPARK":  "ここに火花（火）の熱い気が加わり、情熱的で即時的なエネルギーがこの傾向を押し進めます。",
            "GROUND": "ここに大地（土）の安定した気が加わり、慎重かつどっしりと基盤を築く方向へと発現します。",
            "EDGE":   "ここに鋭さ（金）の気が加わり、明確な基準と鋭い決断力でこの状況を整理していきます。",
            "FLOW":   "ここに流れ（水）の柔軟な気が加わり、状況に応じて賢く柔軟に対処する力が生まれます。",
        },
        "BY_MODE_SECTION": {
            "love": {
                "THE_TWIN":  "特に「相棒」モードが強く、パートナーを生涯の同僚であり対等な仲間として扱います。",
                "THE_RIVAL": "特に「ライバル」モードが強く、互いに刺激し合い共に成長する関係を望みます。",
                "THE_ALLY":  "特に「味方」モードが強く、一度結んだ縁は最後まで責任を持ち尽くします。",
            },
            "career": {
                "THE_CREATOR":    "特に「創造者」モードが強く、既存の枠を壊し自分だけの独創的な成果物を作り出す仕事で輝きます。",
                "THE_OFFICER":    "特に「原理主義者」モードが強く、体系化された組織で信頼される中核人材として成長します。",
                "THE_CHALLENGER": "特に「挑戦者」モードが強く、問題を解決し危機を突破するリーダーの気質があります。",
            },
            "wealth": {
                "THE_OPERATOR": "特に「運営者」モードが強く、他人が見逃す機会を捉え果敢に資産を増やしていきます。",
                "THE_STEWARD":  "特に「管理人」モードが強く、一度集めた資産を安全に守り複利で増やす能力に優れています。",
                "THE_FLOW":     "特に「流れ」モードが強く、執着せず柔軟にお金の流れに乗って自然に富を引き寄せます。",
            },
        },
    },
}


# ─────────────────────────────────────────────────────────
# 3. sections.json (메타데이터 + DISCLAIMER 만)
# ─────────────────────────────────────────────────────────
SECTIONS_JA = {
    "SECTION_TITLES": {
        "cover": "あなたの命式", "core": "あなたの本質",
        "energy": "あなたのエネルギーマップ",
        "lucky_code": "あなたに必要な気",
        "health": "心と体", "money": "富とお金",
        "work": "仕事と才能", "bonds": "友人と同僚",
        "year": "今年の流れ", "timeline": "人生の軌跡",
        "monthly": "月ごとの流れ", "chart": "あなたの4つの顔",
        "sinsal": "特別な才能",
    },
    "SUMMARY_LABELS": {
        "core": "本質", "energy": "エネルギー",
        "lucky_code": "必要な気", "money": "富のモード",
        "bonds": "友人", "year": "今年",
        "health": "体", "monthly": "月ごと",
    },
    "INTENSITY_LABELS": {
        "SELF_SOURCED": "セルフソース型",
        "BALANCED_CORE": "バランスコア型",
        "ENVIRONMENT_TUNED": "環境反応型",
    },
    "MODE_DISPLAY": {
        "THE_PIONEER": "大木 (Pioneer)", "THE_ADAPTER": "蔦 (Adapter)",
        "THE_RADIATOR": "太陽 (Radiator)", "THE_KEEPER": "灯火 (Keeper)",
        "THE_ANCHOR": "山 (Anchor)", "THE_CULTIVATOR": "庭 (Cultivator)",
        "THE_BLADE": "刃 (Blade)", "THE_GEM": "宝石 (Gem)",
        "THE_DEEP": "海 (Deep)", "THE_SPRING": "泉 (Spring)",
        "THE_STEWARD": "管理人 (Steward)", "THE_OPERATOR": "運営者 (Operator)",
        "THE_FLOW": "流れ (Flow)", "THE_CREATOR": "創造者 (Creator)",
        "THE_CHALLENGER": "挑戦者 (Challenger)",
        "THE_OFFICER": "原理主義者 (Officer)",
        "THE_SURVIVOR": "生存者 (Survivor)", "THE_MYSTIC": "探究者 (Mystic)",
        "THE_MENTOR": "メンター (Mentor)",
        "THE_GENERALIST": "オールラウンダー (Generalist)",
        "THE_TWIN": "相棒 (Twin)", "THE_RIVAL": "ライバル (Rival)",
        "THE_ALLY": "味方 (Ally)", "THE_EMPATH": "共感者 (Empath)",
    },
    "ENERGY_HERO_TEMPLATES": {
        "missing": "あなたは{dominant}の気がとても強い代わりに、{missing}の気はほとんどありません。",
        "deficient": "あなたは{dominant}の気が溢れていますが、{deficient}の気はやや不足しています。",
        "default": "あなたは{dominant}の気が中心となっています。",
    },
    "TIMELINE_HERO": (
        "最も強い時期は{best_age}歳ごろ（{best_pillar}）に始まります。"
        "最も難しい時期は{worst_age}歳ごろです。"
    ),
    "TIMELINE_GRADE_BLURB": {
        "PEAK": "稀な機会です。計画的に活用してください。",
        "FAVORABLE": "追い風です。流れに乗ってください。",
        "NEUTRAL": "混在する時期。実際に機能しているものに集中してください。",
        "CAUTION": "ゆっくりした季節。休息と境界線を優先してください。",
        "CHALLENGING": "重い時期。うまく耐え抜けば成長します。",
    },
    "LUCKY_CODE_HERO_TEMPLATE": "今あなたに最も必要な気は{element}です。日常でこの気を満たしてみましょう。",
    "WATCH_OUT_LABEL": "注意",
    "HEALTH_HERO_TEMPLATES": {
        "missing": "{dominant}の気が体を支配しています。一方、{missing}の気はほとんどありません。",
        "deficient": "あなたの体は{dominant}の気に導かれています。一方、{deficient}の気は不足気味です。",
        "default": "{dominant}の気があなたの体を導いています。",
    },
    "CHART_POSITION_TEMPLATES": {
        "year_pillar": "幼少期と家族の影響により、あなたは「{archetype}」の気質を授かりました。",
        "month_pillar": "社会生活や職場で、あなたは「{archetype}」のように振る舞い、頭角を現します。",
        "day_pillar": "あなたの最も深い内面であり本質は「{archetype}」です。",
        "hour_pillar": "年を重ねるほど、また内面の奥深くでは「{archetype}」の姿が現れます。",
    },
    "CHART_NOTE_TEMPLATE": (
        "あなたの{a}と{b}はどちらも「{archetype}」です。"
        "これは、仕事中でも一人でいる時でも、あなたの姿が同じであることを意味します。"
        "「職場の私」と「本当の私」が分離していないため、常に誠実で一貫していますが、"
        "仕事と日常の境界が曖昧になり、疲れやすくなることがあります。"
    ),
    "DISCLAIMER": (
        "ご案内：本レポートは、天文計算と現代の心理コーチングを組み合わせ、"
        "自己理解と娯楽を目的として提供されるものです。"
        "医療・金融・心理カウンセリングではありません。"
        "四柱推命の解釈は流派によって異なる結論に至ることがあります — "
        "たとえば、ある流派は今不足している気を補う方向を、"
        "別の流派は季節のバランスを重視します。"
        "どちらが間違っているわけではありません。"
        "このレポートを一つの視点として受け止め、"
        "人生の決定はご自身でなさることをお勧めします。"
        "危機的な状況であれば、地域の救急サービスや自殺予防ホットラインに"
        "連絡してください。地域別のホットラインは "
        "https://findahelpline.com/ で確認できます。"
    ),
}


# ─────────────────────────────────────────────────────────
# 4. year.json (DEFAULT + NOTE 만)
# ─────────────────────────────────────────────────────────
YEAR_JA = {
    "DEFAULT_YEAR_THEME": {
        "name": "展開する年",
        "headline": "まだ形を成していく途中の年です。",
        "body": (
            "この年の気を一つのパターンに絞ることは難しいです。"
            "注意深く見守ってください — 進むにつれてテーマが明らかになります。"
        ),
        "watch_for": "今年が何かをすでに知っていると決めつけること。",
        "lean_into": "実際に起きていることへの好奇心。",
    },
    "SOLAR_CALENDAR_NOTE": (
        "上記の年は節気年（立春から立春まで）の基準です。"
        "1月にはまだ前年の節気年が適用されます。"
    ),
}


# ─────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────
def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict) -> None:
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(payload)  # 유효성 검증 (실패 시 raise)
    path.write_text(payload, encoding="utf-8")


def override_file(name: str, override: dict) -> None:
    path = JA / name
    if not path.exists():
        print(f"  [ERR] {name}: 파일 없음 — 먼저 백필 필요")
        failed.append(name)
        return
    data = load_json(path)
    changed = False
    for key, value in override.items():
        if data.get(key) == value:
            continue
        data[key] = value
        changed = True
    if not changed:
        print(f"  [SKIP] {name}: 이미 번역 반영됨")
        skipped.append(name)
        return
    save_json(path, data)
    print(f"  [OK] {name}")
    files_written.append(name)


def verify() -> bool:
    print("\n[verify] 스팟 체크 (loader 경유)")
    sys.path.insert(0, str(ROOT))
    from app.services.content.loader import load_pack

    ok = True
    try:
        e = load_pack("ja", "errors")
        if "曖昧です" in e.get("DST_AMBIGUOUS", ""):
            print("  [OK] errors.DST_AMBIGUOUS → Japanese")
        else:
            print(f"  [ERR] errors: {e.get('DST_AMBIGUOUS', '')[:60]!r}")
            ok = False
    except Exception as exc:
        print(f"  [ERR] load errors: {exc}")
        ok = False

    try:
        L = load_pack("ja", "labels")
        if L.get("GRADE_LABELS", {}).get("PEAK") == "最高":
            print("  [OK] labels.GRADE_LABELS.PEAK → 最高")
        else:
            print(f"  [ERR] labels.PEAK: {L.get('GRADE_LABELS', {}).get('PEAK')!r}")
            ok = False
    except Exception as exc:
        print(f"  [ERR] load labels: {exc}")
        ok = False

    try:
        s = load_pack("ja", "sections")
        if s.get("SECTION_TITLES", {}).get("core") == "あなたの本質":
            print("  [OK] sections.SECTION_TITLES.core → あなたの本質")
        else:
            print(f"  [ERR] sections.core: {s.get('SECTION_TITLES', {}).get('core')!r}")
            ok = False
        # DISCLAIMER 스팟
        if "四柱推命" in s.get("DISCLAIMER", ""):
            print("  [OK] sections.DISCLAIMER → Japanese")
        else:
            print("  [ERR] sections.DISCLAIMER not Japanese")
            ok = False
        # 의도된 잔여(영어) 체크
        money = s.get("MONEY_CONTENT", {}).get("THE_STEWARD", {}).get("headline", "")
        if "protect your assets" in money.lower():
            print("  [OK] sections.MONEY_CONTENT 영어 유지 (Phase 2 대상, 의도)")
    except Exception as exc:
        print(f"  [ERR] load sections: {exc}")
        ok = False

    try:
        y = load_pack("ja", "year")
        if y.get("DEFAULT_YEAR_THEME", {}).get("name") == "展開する年":
            print("  [OK] year.DEFAULT_YEAR_THEME.name → 展開する年")
        else:
            print(f"  [ERR] year DEFAULT name: {y.get('DEFAULT_YEAR_THEME', {}).get('name')!r}")
            ok = False
        if "立春から立春" in y.get("SOLAR_CALENDAR_NOTE", ""):
            print("  [OK] year.SOLAR_CALENDAR_NOTE → Japanese")
        else:
            print("  [ERR] year.SOLAR_CALENDAR_NOTE not Japanese")
            ok = False
        # 의도된 잔여(영어) 체크
        ytc = y.get("YEAR_THEME_CONTENT", {}).get("TEN_GOD_FRIEND")
        if ytc and isinstance(ytc, list) and ytc[0].get("name", "").startswith("The "):
            print("  [OK] year.YEAR_THEME_CONTENT 영어 유지 (Phase 2 대상, 의도)")
    except Exception as exc:
        print(f"  [ERR] load year: {exc}")
        ok = False

    return ok


def main() -> int:
    print("=" * 60)
    print("[Phase 1 — JA] 기반 팩 번역")
    print("=" * 60)

    if not JA.exists():
        print(f"[ERR] {JA} 없음 — 백필 상태 확인 필요")
        return 1

    print("\n[1/4] errors.json")
    override_file("errors.json", ERRORS_JA)

    print("\n[2/4] labels.json")
    override_file("labels.json", LABELS_JA)

    print("\n[3/4] sections.json (metadata + DISCLAIMER)")
    override_file("sections.json", SECTIONS_JA)

    print("\n[4/4] year.json (DEFAULT + NOTE)")
    override_file("year.json", YEAR_JA)

    print("\n" + "=" * 60)
    print(f"결과: written={len(files_written)} / skipped={len(skipped)} / failed={len(failed)}")
    print("=" * 60)

    ok = verify() and not failed
    if ok:
        print("\n[Phase 1 OK] 다음:")
        print("  python -m pytest -q")
        print('  git add -A; git commit -m "i18n(ja): phase 1 — errors/labels/sections-meta/year-meta"')
    else:
        print("\n[Phase 1 FAIL] 위 로그 확인")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())