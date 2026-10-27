#!/usr/bin/env python3
"""
Phase 5-2: JA health.json (32 units)
- HEALTH_DISPLAY:    5 keys
- HEALTH_CONTENT:    5 elements × {over_pattern, under_pattern, practices[3]}
- HEALTH_DISCLAIMER:     1
- HEALTH_FRAMEWORK_NOTE: 1

Idempotency: "현재 값 == 영문 원문" 이면 번역, 아니면 skip.
             (한자-only 라벨도 정상 통과 — 영문 비교 기반)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JA = ROOT / "app" / "services" / "content" / "data" / "ja" / "health.json"
EN = ROOT / "app" / "services" / "content" / "data" / "en" / "health.json"

ELEMENTS = ("GROWTH", "SPARK", "GROUND", "EDGE", "FLOW")

DISPLAY_JA = {
    "GROWTH": "成長",
    "SPARK":  "火花",
    "GROUND": "大地",
    "EDGE":   "鋭さ",
    "FLOW":   "流れ",
}

CONTENT_JA = {
    "GROWTH": {
        "over_pattern": (
            "成長のエネルギーが優勢なとき、あなたは前進の勢いで走ります。"
            "課題は「始めること」ではなく「止まること」です。"
            "休息は自分の野心への裏切りに感じられ、静止は停滞のように見えるかもしれません。"
        ),
        "under_pattern": (
            "成長のエネルギーが希薄なとき、始めること自体に苦労するかもしれません"
            "——心でも体でも。スタートを切るのは、"
            "コンクリートを押し進めるような感覚になることがあります。"
        ),
        "practices": [
            "目的のない10分の散歩をしてみましょう。運動ではなく、ただの移動として。",
            "今週、小さなことひとつに「いいえ」と言ってみましょう。その感覚を観察してください。",
            "寝る前に、ゆっくり目的のないストレッチを。直すのではなく、ただ感じるために。",
        ],
    },
    "SPARK": {
        "over_pattern": (
            "火花のエネルギーが優勢なとき、あなたは熱く走ります。"
            "アイデア、感情、熱意が最大音量でやってきます。"
            "リスクは、外へ注ぎすぎて自分の分が残らなくなることです。"
        ),
        "under_pattern": (
            "火花のエネルギーが希薄なとき、やる気が遠く感じられることがあります。"
            "熱意を演じるタイプではなく、あなたの温もりは誰よりも静かです。"
        ),
        "practices": [
            "朝、スマホを見る前に10分だけ静かに過ごしましょう。",
            "今日の小さな喜びをひとつ見つけて、声に出してみましょう。",
            "一週間だけ、夜9時以降の予定を入れずに過ごしてみましょう。",
        ],
    },
    "GROUND": {
        "over_pattern": (
            "大地のエネルギーが優勢なとき、あなたは誰かが寄りかかる存在になります。"
            "リスクは、あまりに多くをあまりに長く抱え、"
            "自分の重さを忘れてしまうことです。"
        ),
        "under_pattern": (
            "大地のエネルギーが希薄なとき、地に足がつかない感覚を覚えるかもしれません"
            "——外から見れば何も問題なく見えても、"
            "いつもどこか均衡を失っているような感覚。"
        ),
        "practices": [
            "一日一食はゆっくり、座って、画面を見ずに食べましょう。",
            "裸足で本物の大地に5分間立ってみましょう。",
            "三日間続けて、同じ時刻に食事をとりましょう。",
        ],
    },
    "EDGE": {
        "over_pattern": (
            "鋭さのエネルギーが優勢なとき、あなたは雑音を切り裂きます。"
            "リスクは、論点を取って場を失うこと、"
            "あるいはその鋭さを自分自身に向けてしまうことです。"
        ),
        "under_pattern": (
            "鋭さのエネルギーが希薄なとき、"
            "正しい判断でも衝突を避けてしまうことがあります。"
            "境界を引くのが、本来より難しく感じられるかもしれません。"
        ),
        "practices": [
            "メールを開く前に、ゆっくり深く呼吸を三回。",
            "今日、小さな面をひとつ片づけましょう——机、引き出し、リスト。",
            "寒くても、外で10分過ごしましょう。",
        ],
    },
    "FLOW": {
        "over_pattern": (
            "流れのエネルギーが優勢なとき、あなたは容易に適応します。"
            "リスクは、なかなか本気でコミットできないこと"
            "——すべてがまだ可能だからです。"
        ),
        "under_pattern": (
            "流れのエネルギーが希薄なとき、"
            "動く前に物事がどこへ向かうかを知りたいと願います。"
            "その慎重さは有用ですが——檻になるまでは。"
        ),
        "practices": [
            "毎食前にコップ一杯の水を飲みましょう。",
            "今月、何も産まない完全な休息の日を一日取りましょう。",
            "未解決の問いと共に、5分間静かに座ってみましょう。答えは要りません。",
        ],
    },
}

DISCLAIMER_JA = (
    "このセクションは、伝統的な五行思想から着想を得た"
    "ライフスタイルの省察を提供します。"
    "これは医療上の助言、診断、治療ではありません。"
    "健康に関する懸念がある場合は、"
    "資格を持つ医療専門家にご相談ください。"
)

FRAMEWORK_NOTE_JA = (
    "枠組み：五行（五行）思想——自己省察とパーソナルインサイトのための"
    "伝統的なレンズです。臨床的なガイドラインではありません。"
    "解釈は流派によって異なります。"
)


def main() -> int:
    ja_data = json.loads(JA.read_text(encoding="utf-8"))
    en_data = json.loads(EN.read_text(encoding="utf-8"))

    en_display  = en_data.get("HEALTH_DISPLAY", {})
    en_content  = en_data.get("HEALTH_CONTENT", {})
    en_disc     = en_data.get("HEALTH_DISCLAIMER", "")
    en_note     = en_data.get("HEALTH_FRAMEWORK_NOTE", "")

    applied = skipped = 0

    # ---- HEALTH_DISPLAY ----
    display = ja_data.setdefault("HEALTH_DISPLAY", {})
    for k in ELEMENTS:
        if display.get(k) == en_display.get(k):
            display[k] = DISPLAY_JA[k]
            print(f"✅ DISPLAY.{k}: {DISPLAY_JA[k]}")
            applied += 1
        else:
            print(f"⏭️  DISPLAY.{k}: 이미 번역됨 ({display.get(k)})")
            skipped += 1

    # ---- HEALTH_CONTENT ----
    content = ja_data.setdefault("HEALTH_CONTENT", {})
    for elem in ELEMENTS:
        block = content.setdefault(elem, {})
        en_block = en_content.get(elem, {})

        for field in ("over_pattern", "under_pattern"):
            if block.get(field) == en_block.get(field):
                block[field] = CONTENT_JA[elem][field]
                print(f"✅ CONTENT.{elem}.{field}")
                applied += 1
            else:
                print(f"⏭️  CONTENT.{elem}.{field}: 이미 번역됨")
                skipped += 1

        # practices (리스트)
        if block.get("practices") == en_block.get("practices"):
            block["practices"] = CONTENT_JA[elem]["practices"]
            print(f"✅ CONTENT.{elem}.practices[3]")
            applied += 1
        else:
            print(f"⏭️  CONTENT.{elem}.practices: 이미 번역됨")
            skipped += 1

    # ---- HEALTH_DISCLAIMER ----
    if ja_data.get("HEALTH_DISCLAIMER") == en_disc:
        ja_data["HEALTH_DISCLAIMER"] = DISCLAIMER_JA
        print("✅ HEALTH_DISCLAIMER")
        applied += 1
    else:
        print("⏭️  HEALTH_DISCLAIMER: 이미 번역됨")
        skipped += 1

    # ---- HEALTH_FRAMEWORK_NOTE ----
    if ja_data.get("HEALTH_FRAMEWORK_NOTE") == en_note:
        ja_data["HEALTH_FRAMEWORK_NOTE"] = FRAMEWORK_NOTE_JA
        print("✅ HEALTH_FRAMEWORK_NOTE")
        applied += 1
    else:
        print("⏭️  HEALTH_FRAMEWORK_NOTE: 이미 번역됨")
        skipped += 1

    # ---- 저장 전 사전검증 ----
    payload = json.dumps(ja_data, ensure_ascii=False, indent=2) + "\n"
    json.loads(payload)
    JA.write_text(payload, encoding="utf-8")

    print(f"\n결과: applied={applied}, skipped={skipped}")

    # ---- 검증 (영문 원문과 다른가?) ----
    print("\n[verify]")
    data = json.loads(JA.read_text(encoding="utf-8"))
    all_ok = True

    for elem in ELEMENTS:
        d_ok = data["HEALTH_DISPLAY"].get(elem) != en_display.get(elem)
        o_ok = data["HEALTH_CONTENT"][elem].get("over_pattern")  != en_content.get(elem, {}).get("over_pattern")
        u_ok = data["HEALTH_CONTENT"][elem].get("under_pattern") != en_content.get(elem, {}).get("under_pattern")
        p_ok = data["HEALTH_CONTENT"][elem].get("practices")     != en_content.get(elem, {}).get("practices")
        if d_ok and o_ok and u_ok and p_ok:
            print(f"  ✅ {elem}: display/over/under/practices = JA")
        else:
            print(f"  ❌ {elem}: display={d_ok} over={o_ok} under={u_ok} practices={p_ok}")
            all_ok = False

    disc_ok = data.get("HEALTH_DISCLAIMER") != en_disc
    note_ok = data.get("HEALTH_FRAMEWORK_NOTE") != en_note
    if disc_ok and note_ok:
        print("  ✅ DISCLAIMER / FRAMEWORK_NOTE = JA")
    else:
        print(f"  ❌ DISCLAIMER={disc_ok} FRAMEWORK_NOTE={note_ok}")
        all_ok = False

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())