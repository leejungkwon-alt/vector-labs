#!/usr/bin/env python3
"""
Phase 5-4: JA age_band.json (25 units)
- AGE_BAND_CONTENT: 5 bands × {label, headline, body, advice[3]}

Idempotency: "현재 값 == 영문 원문" 이면 번역, 아니면 skip.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JA = ROOT / "app" / "services" / "content" / "data" / "ja" / "age_band.json"
EN = ROOT / "app" / "services" / "content" / "data" / "en" / "age_band.json"

BANDS = ("EARLY", "MID", "PEAK", "SENIOR", "ELDER")

BAND_JA = {
    "EARLY": {
        "label": "探索期",
        "headline": "今は人生の探索期です。",
        "body": (
            "今は正解を当てる時ではなく、データを集める時です。"
            "何が自分を生かし、何が自分を疲れさせるのか——"
            "誰も見ていないときに自分が何を選ぶのか、"
            "それを知っていくプロセスです。"
            "今の選択は生涯を縛る契約ではなく、"
            "気軽な実験だと思って構いません。"
        ),
        "advice": [
            "この四半期に、少し怖いことをひとつ試してみましょう。",
            "紙の上で立派に見えることではなく、実際に自分を高揚させるものを記録しましょう。",
            "今は広く経験しましょう。深くなるのは後でもできます。",
        ],
    },
    "MID": {
        "label": "蓄積期",
        "headline": "今は人生の蓄積期です。",
        "body": (
            "今蒔く種には、根を張るだけの十分な時間があります。"
            "リターンが遅く感じられるのは、実際に遅いから——"
            "そしてそれこそが複利で積み上がる理由です。"
            "この季節の課題は、深く掘る価値のあるいくつかを選び、"
            "手放したものについてもう謝らないことです。"
        ),
        "advice": [
            "スキルひとつ、関係ひとつ、資産ひとつだけ選んで深く掘りましょう。",
            "長いゲームに奉仕しない三つのことに、潔く「いいえ」と言いましょう。",
            "5年後にはじめて報われる何かを、ひとつ始めましょう。",
        ],
    },
    "PEAK": {
        "label": "全盛期",
        "headline": "今は人生の全盛期です。",
        "body": (
            "世界があなたの成果物を求めています。"
            "危険なのは怠惰ではなく「過剰拡張」。"
            "誰もがあなたのエネルギーを欲しがります。"
            "今放つものがこの先10年の評判を決めます。"
            "あなたの体力を削らずに済む余白を、"
            "意識して守ってください。"
        ),
        "advice": [
            "あなたにしかできないことを中心に一週間を設計しましょう。",
            "それ以外のことは潔く委任するか、捨てましょう。",
            "週に一日は完全にあなただけの時間として空けておきましょう。",
        ],
    },
    "SENIOR": {
        "label": "収穫期",
        "headline": "今は人生の収穫期です。",
        "body": (
            "「する」から「導く」へ、成果から知恵へ移動する時期です。"
            "今のあなたの価値は、注ぎ込む時間ではなく、"
            "積み上げてきた判断力から生まれます。"
            "周りの人はあなたの労働よりも、"
            "あなたの深い視点を必要としています。"
        ),
        "advice": [
            "一人で抱えていた仕事をひとつ、メンティーに渡して教えましょう。",
            "長く語って構いません。今、あなたの話を聞こうとする人がいます。",
            "何年も心に抱えていた荷物をひとつ、下ろしましょう。",
        ],
    },
    "ELDER": {
        "label": "存在期",
        "headline": "今は人生の存在期です。",
        "body": (
            "生産性よりも存在そのものが大切になる時期です。"
            "残すものはすでに植え終えました。"
            "今の課題は、どう存在するか——"
            "後に来る人たちに、そしてまだ育っている"
            "自分の内面に向き合うことです。"
        ),
        "advice": [
            "あなただけが知っていることを、ひとつ書き残しましょう。",
            "若い人と、先生ではなく対等な仲間として時間を過ごしましょう。",
            "毎日をしっかり支えてくれる小さな習慣をひとつ選びましょう。",
        ],
    },
}

FIELDS = ("label", "headline", "body", "advice")


def main() -> int:
    ja_data = json.loads(JA.read_text(encoding="utf-8"))
    en_data = json.loads(EN.read_text(encoding="utf-8"))

    en_content = en_data.get("AGE_BAND_CONTENT", {})
    ja_content = ja_data.setdefault("AGE_BAND_CONTENT", {})

    applied = skipped = 0

    for band in BANDS:
        ja_block = ja_content.setdefault(band, {})
        en_block = en_content.get(band, {})

        for field in FIELDS:
            if ja_block.get(field) == en_block.get(field):
                ja_block[field] = BAND_JA[band][field]
                tag = "advice[3]" if field == "advice" else field
                print(f"✅ {band}.{tag}")
                applied += 1
            else:
                tag = "advice[3]" if field == "advice" else field
                print(f"⏭️  {band}.{tag}: 이미 번역됨")
                skipped += 1

    # 저장 전 사전검증
    payload = json.dumps(ja_data, ensure_ascii=False, indent=2) + "\n"
    json.loads(payload)
    JA.write_text(payload, encoding="utf-8")

    print(f"\n결과: applied={applied}, skipped={skipped}")

    # 검증
    print("\n[verify]")
    data = json.loads(JA.read_text(encoding="utf-8"))
    ja_c = data["AGE_BAND_CONTENT"]
    all_ok = True
    for band in BANDS:
        fields_ok = all(
            ja_c[band].get(f) != en_content.get(band, {}).get(f)
            for f in FIELDS
        )
        advice_ok = isinstance(ja_c[band].get("advice"), list) and len(ja_c[band]["advice"]) == 3
        if fields_ok and advice_ok:
            print(f"  ✅ {band}: {ja_c[band]['label']} / 4-fields = JA / advice[3]")
        else:
            print(f"  ❌ {band}: fields={fields_ok} advice={advice_ok}")
            all_ok = False

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())