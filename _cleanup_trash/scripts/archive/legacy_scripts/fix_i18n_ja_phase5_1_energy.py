#!/usr/bin/env python3
"""
Phase 5-1: JA energy.json (35 units)
- ELEMENT_DISPLAY: 5개 (GROWTH/SPARK/GROUND/EDGE/FLOW)
- ELEMENT_KEYWORDS: 5개 × 3 키워드
- ELEMENT_CONTENT: 5개 × 3 필드 (on_dominant / on_deficient / on_missing)

Idempotency: "현재 값 == 영문 원문" 이면 번역, 아니면 skip.
             (한자만으로 된 라벨도 정상 통과 — GRADE_LABEL 오탐 회피)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JA = ROOT / "app" / "services" / "content" / "data" / "ja" / "energy.json"
EN = ROOT / "app" / "services" / "content" / "data" / "en" / "energy.json"


DISPLAY_JA = {
    "GROWTH": "成長",
    "SPARK":  "火花",
    "GROUND": "大地",
    "EDGE":   "鋭さ",
    "FLOW":   "流れ",
}

KEYWORDS_JA = {
    "GROWTH": ["拡張", "方向", "主導"],
    "SPARK":  ["表現", "温もり", "可視性"],
    "GROUND": ["安定", "信頼", "忍耐"],
    "EDGE":   ["明晰", "構造", "精密"],
    "FLOW":   ["適応", "知恵", "深さ"],
}

CONTENT_JA = {
    "GROWTH": {
        "on_dominant":  "あなたは成長のエネルギーが溢れています。それは絶え間ない前進として現れ、物事を簡単に始められ、なかなか「終わった」と感じません。",
        "on_deficient": "成長はあなたの最も希少なエネルギーのひとつです。明確な理由がなければ物事を始めにくく、新鮮さが薄れると育て続けるのも難しくなります。",
        "on_missing":   "あなたの命式には成長のエネルギーがほとんどありません。これは欠陥ではなく、異なる中心から動いているという意味です。「拡張のための拡張」があなたを動機づけることは決してありません。",
    },
    "SPARK": {
        "on_dominant":  "あなたの命式は火の気が強いです。熱く走り、目に見えて光を放ち、繊細さとは無縁です。リスクは燃え尽き——誰もがその温もりの一部を欲しがります。",
        "on_deficient": "火花はあなたの最も希少なエネルギーのひとつです。熱意を演じることはなく、音量を求めるタイプではありません。あなたの温もりは誰よりも静かです。",
        "on_missing":   "火花のエネルギーはほとんどありません。あなたはそれを持つ人に惹かれます——その人が、あなたの静かな仕事を可視化してくれる光なのです。",
    },
    "GROUND": {
        "on_dominant":  "あなたは深い大地のエネルギーを持っています。人が寄りかかる存在で、しかも本人はそれに気づいていません。リスクは、あまりに多くをあまりに長く抱え続けることです。",
        "on_deficient": "大地はあなたの最も希少なエネルギーのひとつです。じっとしていることや、ゆっくりした進歩と折り合うことに苦労します。認める以上に動き回っているはずです。",
        "on_missing":   "大地のエネルギーはほとんどありません。安定はあなたのデフォルト状態ではありません——落ち着くのではなく、動くことで足場を見つけるタイプです。",
    },
    "EDGE": {
        "on_dominant":  "あなたの命式は金の気が強いです。雑音を切り裂きます。好かれることより正しいことを選び、たいてい正しい。リスクは、論点を取って場を失うことです。",
        "on_deficient": "鋭さはあなたの最も希少なエネルギーのひとつです。正しい判断でも衝突を避け、柔らげる必要のないものまで柔らげてしまいます。",
        "on_missing":   "鋭さのエネルギーはほとんどありません。構造と精密さを先頭に立てるのではなく、もっと温かい何かで人を導きます。それは弱さではありません。",
    },
    "FLOW": {
        "on_dominant":  "あなたの命式は水の気が強いです。容易に動き、容易に適応し、待つべきときを知っています。リスクは、すべてが可能だからこそ、どれにも本気でコミットできなくなることです。",
        "on_deficient": "流れはあなたの最も希少なエネルギーのひとつです。流れに身を任せるのが難しく、動く前にどこへ向かうかを知りたいと願います。",
        "on_missing":   "流れのエネルギーはほとんどありません。漂うのではなく、決めます。これは危機のときに頼りになりますが、適応力を求められる場面では硬く感じられることがあります。",
    },
}

ELEMENTS = ("GROWTH", "SPARK", "GROUND", "EDGE", "FLOW")
FIELDS = ("on_dominant", "on_deficient", "on_missing")


def main() -> int:
    ja_data = json.loads(JA.read_text(encoding="utf-8"))
    en_data = json.loads(EN.read_text(encoding="utf-8"))

    en_display  = en_data.get("ELEMENT_DISPLAY", {})
    en_kws      = en_data.get("ELEMENT_KEYWORDS", {})
    en_content  = en_data.get("ELEMENT_CONTENT", {})

    applied = skipped = 0

    # ---- ELEMENT_DISPLAY ----
    display = ja_data.setdefault("ELEMENT_DISPLAY", {})
    for k in ELEMENTS:
        if display.get(k) == en_display.get(k):  # 영문 그대로 → 번역
            display[k] = DISPLAY_JA[k]
            print(f"✅ DISPLAY.{k}: {DISPLAY_JA[k]}")
            applied += 1
        else:
            print(f"⏭️  DISPLAY.{k}: 이미 번역됨 ({display.get(k)})")
            skipped += 1

    # ---- ELEMENT_KEYWORDS ----
    kws = ja_data.setdefault("ELEMENT_KEYWORDS", {})
    for k in ELEMENTS:
        if kws.get(k) == en_kws.get(k):  # 리스트 동등성 비교
            kws[k] = KEYWORDS_JA[k]
            print(f"✅ KEYWORDS.{k}: {KEYWORDS_JA[k]}")
            applied += 1
        else:
            print(f"⏭️  KEYWORDS.{k}: 이미 번역됨")
            skipped += 1

    # ---- ELEMENT_CONTENT ----
    content = ja_data.setdefault("ELEMENT_CONTENT", {})
    for elem in ELEMENTS:
        block = content.setdefault(elem, {})
        en_block = en_content.get(elem, {})
        for field in FIELDS:
            if block.get(field) == en_block.get(field):
                block[field] = CONTENT_JA[elem][field]
                print(f"✅ CONTENT.{elem}.{field}")
                applied += 1
            else:
                print(f"⏭️  CONTENT.{elem}.{field}: 이미 번역됨")
                skipped += 1

    # ---- 저장 전 사전검증 ----
    payload = json.dumps(ja_data, ensure_ascii=False, indent=2) + "\n"
    json.loads(payload)  # 파싱 실패하면 저장 안 함
    JA.write_text(payload, encoding="utf-8")

    print(f"\n결과: applied={applied}, skipped={skipped}")

    # ---- 검증: 영문 원문과 다르면 통과 (kana 요구 X, 한자-only도 OK) ----
    print("\n[verify]")
    data = json.loads(JA.read_text(encoding="utf-8"))
    all_ok = True
    for k in ELEMENTS:
        display_ok = data["ELEMENT_DISPLAY"].get(k) != en_display.get(k)
        kws_ok     = data["ELEMENT_KEYWORDS"].get(k) != en_kws.get(k)
        fields_ok  = all(
            data["ELEMENT_CONTENT"][k].get(f) != en_content.get(k, {}).get(f)
            for f in FIELDS
        )
        if display_ok and kws_ok and fields_ok:
            print(f"  ✅ {k}: display/3-kw/3-fields = JA")
        else:
            print(f"  ❌ {k}: display={display_ok} kw={kws_ok} content={fields_ok}")
            all_ok = False

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())