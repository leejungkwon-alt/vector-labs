#!/usr/bin/env python3
"""Phase 4-20: JA personalization.json (32 fields) + telegram.json (1)."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "app" / "services" / "content" / "data" / "ja"
JA_PERSON = DATA / "personalization.json"
JA_TG     = DATA / "telegram.json"
KANA_RE = re.compile(r'[\u3040-\u30FF]')

PERSON = {
    "ELEMENT_DOMINANT": {
        "GROWTH": "あなたの圧倒的な成長（木）の気は、新しいことを始める止まらない推進力になります。ただし、ときに落ち着きを失わせます。",
        "SPARK": "あなたの激しい火花（火）の気は、あなたをとても目立たせ磁力的にしますが、燃え尽きのリスクを伴います。",
        "GROUND": "あなたの重厚な大地（土）の気は、他者にとって頼りになる錨にしますが、重荷を抱えすぎるかもしれません。",
        "EDGE": "あなたの鋭い刃（金）の気は、外科的な明晰さを与えますが、切り込みすぎないよう注意が必要です。",
        "FLOW": "あなたの深い流れ（水）の気は、深遠な適応力と知恵を与えますが、コミットすることに苦労するかもしれません。",
    },
    "ELEMENT_DEFICIENT": {
        "GROWTH": "成長の気が乏しいため、明確な後押しがなければ物事を始めるのに苦労します。",
        "SPARK": "火花の気が乏しいため、熱意を無理に演じることはなく、静かな温もりを好みます。",
        "GROUND": "大地の気が欠けているため、拠り所を失ったように感じることがあり、動くことで安定を探します。",
        "EDGE": "刃の気が乏しいため、衝突を自然に避け、境界線を柔らかくします。",
        "FLOW": "流れの気が乏しいため、動く前にどこへ向かうかを正確に把握しておきたいと願います。",
    },
    "GYEOKGUK": {
        "STABILIZER": "安定志向の気質を持ち、システムを構築し維持することに卓越しています。",
        "WARRIOR": "突破する戦士の気質を持ち、衝突に立ち向かい障害を打ち破るのが得意です。",
        "CUSTODIAN": "資源を管理する守護者の気質を持ち、他者を守り育てることに深い意味を見出します。",
        "DEALMAKER": "機会を捉える交渉者の気質を持ち、他人がノイズと呼ぶ場所で機会を見つけます。",
        "EXPRESSER": "表現する者の気質を持ち、抽象的なアイデアを具体的な価値へと変えます。",
        "DISRUPTOR": "革新する破壊者の気質を持ち、既存の慣行に絶えず疑問を投げかけます。",
        "MENTOR": "知識を分かち合うメンターの気質を持ち、他者を導き教えることに喜びを感じます。",
        "INTUITIVE": "直感型の気質を持ち、他人が見落とすつながりを斜めに思考して見つけ出します。",
        "EDGE_WALKER": "境界を歩む者の気質を持ち、秩序と混沌の綱渡りを楽しみます。",
        "COOPERATOR": "仲間と協力する気質を持ち、水平的な連帯から力を得ます。",
        "SELF_MADE": "自助努力の気質を持ち、何よりも自分の汗と努力を信じます。",
    },
    "SINSAL": {
        "MAGNETIC_DRAW": "生まれつきの魅力があり、口を開く前から人の視線を集めます。",
        "RESTLESS_FEET": "旅人の気質が強く、一箇所に留まるよりも動き探検することを楽しみます。",
        "SOLITARY_DEPTH": "深い内面世界を持ち、一人の時間を通じて豊かさを得ます。",
        "ALLY_MAGNET": "周囲に頼れる支援者が多く、困難なときに予想外の助けを受けます。",
        "SCHOLAR_MIND": "知的好奇心に優れ、学びへの生まれつきの渇望と学習能力を備えています。",
        "SHARP_EDGE": "一度勝つと決めたら屈しない、強い勝負欲と推進力を持っています。",
        "COMMANDER": "強い道徳観に基づき、他人がためらうときに先頭に立つ生まれながらのリーダーです。",
    },
    "RELATIONS": {
        "day_chong": "あなたの内面には常に「新しい変化」を渇望するエネルギーが流れています。一箇所に定住するよりも、絶えず動き挑戦するときに真の安定を得るタイプです。",
        "has_chong": "予測不可能な変化と挑戦があなたの人生を貫きます。ときに疲れて感じることもありますが、逆説的にあなたを誰よりも強く独創的な人間にする原動力です。",
    },
    "SPECIAL_CONDITIONS": {
        "RESTLESS_FEET": "あなたは生まれながらの「旅人」です。新しい経験、旅行、転職などを通じてエネルギーを得て成長します。ルーティンに閉じ込められることが最も苦手です。",
        "seven_killings": "あなたは強い「上司」のエネルギーを持っています。支配し、戦略を立て、群れを率いることに卓越しています。プレッシャーや危機の中でむしろ強くなります。",
    },
}

PUSH_CAPTION = (
    "🌅 おはようございます！\n"
    "今日の運気アップデートが届きました。\n"
    "[今日の3D壁紙をダウンロード]({url})"
)

def _ja(s): return bool(s) and bool(KANA_RE.search(s))

def main():
    print("=" * 60); print("[Phase 4-20] personalization + telegram"); print("=" * 60)

    # personalization
    if not JA_PERSON.exists():
        JA_PERSON.parent.mkdir(parents=True, exist_ok=True)
        p_data = {}
        print(f"📄 personalization.json 새로 생성")
    else:
        p_data = json.loads(JA_PERSON.read_text(encoding="utf-8"))
    for block, entries in PERSON.items():
        p_data.setdefault(block, {}).update(entries)
    p_payload = json.dumps(p_data, ensure_ascii=False, indent=2) + "\n"
    json.loads(p_payload)
    JA_PERSON.write_text(p_payload, encoding="utf-8")
    print(f"✅ personalization.json: 6 blocks 저장")

    # telegram
    if not JA_TG.exists():
        JA_TG.parent.mkdir(parents=True, exist_ok=True)
        t_data = {}
        print(f"📄 telegram.json 새로 생성")
    else:
        t_data = json.loads(JA_TG.read_text(encoding="utf-8"))
    t_data["PUSH_DAILY_CAPTION"] = PUSH_CAPTION
    t_payload = json.dumps(t_data, ensure_ascii=False, indent=2) + "\n"
    json.loads(t_payload)
    JA_TG.write_text(t_payload, encoding="utf-8")
    print(f"✅ telegram.json: PUSH_DAILY_CAPTION 저장")

    # verify
    print("\n[verify]")
    ok = True
    for block, entries in PERSON.items():
        for key in entries:
            if not _ja(p_data[block].get(key, "")):
                print(f"  [ERR] {block}.{key}"); ok = False
    if not _ja(t_data.get("PUSH_DAILY_CAPTION", "")):
        print("  [ERR] telegram.PUSH_DAILY_CAPTION"); ok = False
    if ok:
        print("  [OK] personalization 32/32 = JA")
        print("  [OK] telegram 1/1 = JA 🏆")
    print("=" * 60)
    return 0 if ok else 1

if __name__ == "__main__": sys.exit(main())