#!/usr/bin/env python3
"""
Phase 5-3: JA sinsal.json (28 units)
- SINSAL_CONTENT: 7 신살 × {name, headline, body, advice}
- name_traditional: 비어있으면 한자 병기 채움 (桃花/驛馬/華蓋/天乙貴人/文昌貴人/羊刃/魁罡)

Idempotency:
- name/headline/body/advice : "현재 값 == 영문 원문" 이면 번역
- name_traditional          : 빈 문자열이면 채움, 이미 있으면 skip
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JA = ROOT / "app" / "services" / "content" / "data" / "ja" / "sinsal.json"
EN = ROOT / "app" / "services" / "content" / "data" / "en" / "sinsal.json"


SINSAL_JA = {
    "MAGNETIC_DRAW": {
        "name": "引き寄せる魅力",
        "name_traditional": "桃花",
        "headline": "あなたは言葉を発する前から、人の視線を引き寄せる魅力を持っています。",
        "body": (
            "生まれつきの引力があります。これは演じているのではなく、"
            "自然に滲み出る重力のようなもの。人はあなたを記憶し、"
            "そばにいたいと思います。"
        ),
        "advice": (
            "この引力を責任をもって使いましょう。"
            "人を引き寄せても、所有しようとしないこと。"
            "深さは量に勝ります。"
        ),
    },
    "RESTLESS_FEET": {
        "name": "旅人の足",
        "name_traditional": "驛馬",
        "headline": "あなたは動くために生まれています。",
        "body": (
            "一か所に留まることは、体でも心でもあなたを疲れさせます。"
            "旅、探検、新しい学びを通じて生き生きとします。"
        ),
        "advice": (
            "日常に意識的に動きを取り入れましょう。"
            "旅が難しければ、ルーティンを変えてみてください。"
        ),
    },
    "SOLITARY_DEPTH": {
        "name": "静かな省察者",
        "name_traditional": "華蓋",
        "headline": "あなたの内面は、誰でも入れる深い空間ではありません。",
        "body": (
            "静けさ、内省、一人の活動に惹かれます。"
            "創造性と洞察はこの深い井戸から生まれます。"
            "それは孤独ではなく余白です。"
        ),
        "advice": (
            "一人の時間を守りましょう。"
            "贅沢品ではなく、あなたの力の源です。"
        ),
    },
    "ALLY_MAGNET": {
        "name": "頼れる支援者",
        "name_traditional": "天乙貴人",
        "headline": "あなたは助けたいと思ってくれる人を引き寄せます。",
        "body": (
            "メンター、支援者、恩人が自然と集まってきます。"
            "困難なときに予想外の場所から助けが届きます。"
            "とても稀有で貴重な才能です。"
        ),
        "advice": (
            "助けを素直に受け入れましょう。"
            "すべてを一人でやる必要はありません。"
        ),
    },
    "SCHOLAR_MIND": {
        "name": "学びの探究者",
        "name_traditional": "文昌貴人",
        "headline": "知識に対する生まれつきの渇望があります。",
        "body": (
            "情報を深く処理し、学ぶこと自体を愛します。"
            "学び、書き、教えるときに最高の姿を見せます。"
        ),
        "advice": (
            "学びを止めないでください。"
            "あなたの脳こそ最大の資産です。"
        ),
    },
    "SHARP_EDGE": {
        "name": "揺るがない推進力",
        "name_traditional": "羊刃",
        "headline": "あなたは競争心が強く、決して屈しない推進力があります。",
        "body": (
            "野心家で競争心が強く、独立心も強い。"
            "一度勝つと決めたら止まりません。"
            "両刃の剣で、ペースを崩すと燃え尽きる可能性があります。"
        ),
        "advice": (
            "あなたの強さを目標に注ぎましょう。"
            "自分を削るのではなく。"
        ),
    },
    "COMMANDER": {
        "name": "生まれながらの指揮官",
        "name_traditional": "魁罡",
        "headline": "強い道徳観を持つ生まれながらのリーダーです。",
        "body": (
            "他の人がためらうときに先頭に立ちます。"
            "正義感が強く、難しい決断を恐れません。"
            "困難なときに人があなたを訪ねます。"
        ),
        "advice": (
            "共感をもって導きましょう。"
            "親切のない強さは孤立になります。"
        ),
    },
}

FIELDS = ("name", "headline", "body", "advice")


def main() -> int:
    ja_data = json.loads(JA.read_text(encoding="utf-8"))
    en_data = json.loads(EN.read_text(encoding="utf-8"))

    en_content = en_data.get("SINSAL_CONTENT", {})
    ja_content = ja_data.setdefault("SINSAL_CONTENT", {})

    applied = skipped = 0

    for key, trans in SINSAL_JA.items():
        ja_block = ja_content.setdefault(key, {})
        en_block = en_content.get(key, {})

        # ---- name / headline / body / advice : 영문 비교 ----
        for field in FIELDS:
            if ja_block.get(field) == en_block.get(field):
                ja_block[field] = trans[field]
                print(f"✅ {key}.{field}")
                applied += 1
            else:
                print(f"⏭️  {key}.{field}: 이미 번역됨")
                skipped += 1

        # ---- name_traditional : 비어있으면 채움 ----
        current_trad = ja_block.get("name_traditional", "")
        if not current_trad:
            ja_block["name_traditional"] = trans["name_traditional"]
            print(f"✅ {key}.name_traditional: {trans['name_traditional']}")
            applied += 1
        else:
            print(f"⏭️  {key}.name_traditional: 이미 있음 ({current_trad})")
            skipped += 1

    # ---- 저장 전 사전검증 ----
    payload = json.dumps(ja_data, ensure_ascii=False, indent=2) + "\n"
    json.loads(payload)
    JA.write_text(payload, encoding="utf-8")

    print(f"\n결과: applied={applied}, skipped={skipped}")

    # ---- 검증 ----
    print("\n[verify]")
    data = json.loads(JA.read_text(encoding="utf-8"))
    ja_c = data["SINSAL_CONTENT"]
    all_ok = True

    for key in SINSAL_JA:
        fields_ok = all(
            ja_c[key].get(f) != en_content.get(key, {}).get(f)
            for f in FIELDS
        )
        trad_ok = bool(ja_c[key].get("name_traditional"))
        if fields_ok and trad_ok:
            print(f"  ✅ {key}: 4-fields = JA / trad = {ja_c[key]['name_traditional']}")
        else:
            print(f"  ❌ {key}: fields={fields_ok} trad={trad_ok}")
            all_ok = False

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())