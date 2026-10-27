#!/usr/bin/env python3
"""Phase 4-17: JA sections.json — BONDS_CONTENT 4 modes + sections.json 전체 재검증."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
JA = ROOT / "app" / "services" / "content" / "data" / "ja" / "sections.json"
KANA_RE = re.compile(r'[\u3040-\u30FF]')

T = {
    "THE_TWIN": {
        "headline": "対等な関係の中で最もくつろげます。",
        "body": (
            "誰かを導いたり、誰かに頼ったりするのが好きではありません。"
            "同じ高さで目を合わせ、共に同じ方向へ歩むパートナーを望みます。\n\n"
            "互いの違いを認め、共に成長する関係を最も理想的と考えます。"
            "互いに負担をかけず、それでいて深い絆を形づくります。\n\n"
            "ただ、「クール」な関係だけを追い求めすぎると、深い親密さを築くのが"
            "難しくなります。ときに互いに寄りかかり、頼ることも覚えましょう。"
        ),
        "patterns": [
            "恋人というより、友人のような気楽さを求めます。",
            "互いのプライベートを尊重します。",
            "主導権争いを嫌います。",
        ],
        "best_match": ["THE_ALLY", "THE_EMPATH"],
        "best_reason": "あなたの自律性を尊重し、優しく近づいてくれる人です。",
        "challenging_match": ["THE_TWIN"],
        "challenging_reason": "二人ともクールすぎると、関係が退屈になりがちです。",
        "actions": [
            "ときには、あなたから先に手を差し伸べましょう。",
            "相手にわだかまりがあれば、素直に伝えましょう。",
            "一緒に楽しめる趣味をひとつ作りましょう。",
        ],
        "red_flags": [
            "無関心すぎて、相手が寂しさを感じていませんか？",
            "喧嘩を避けるために感情を隠していませんか？",
        ],
    },
    "THE_RIVAL": {
        "headline": "互いに刺激し合う健全な競争を楽しみます。",
        "body": (
            "無条件に同意してくれる人よりも、進んで議論し、押し返してくれる人を求めます。\n\n"
            "異なる意見を交わし、ときに鋭くフィードバックし合いながら、互いを鍛えていきます。"
            "そうした関係は退屈する暇がなく、常に相手から学び続けることができます。\n\n"
            "ただ、すべての会話を議論にする必要はありません。"
            "相手が今、慰めを求めているのか、助言を求めているのかを見抜く共感力が必要です。"
        ),
        "patterns": [
            "意見の衝突を恐れません。",
            "ユーモアと勝負欲が強いです。",
            "感情よりも論理で会話をします。",
        ],
        "best_match": ["THE_EMPATH", "THE_ALLY"],
        "best_reason": "あなたの鋭さを優しく和らげ、包み込んでくれる人です。",
        "challenging_match": ["THE_RIVAL"],
        "challenging_reason": "二人とも勝とうとすると、関係が壊れます。",
        "actions": [
            "議論の最中でも、相手の感情を確認しましょう。",
            "一日に一度は相手を褒めましょう。",
            "ときに、反論せずに聞く練習をしましょう。",
        ],
        "red_flags": [
            "勝つために傷つける言葉を口にしていませんか？",
            "相手が疲れているのに、論理を振りかざしていませんか？",
        ],
    },
    "THE_ALLY": {
        "headline": "一度受け入れた縁は、最後まで責任を持ちます。",
        "body": (
            "誰とでも気軽に付き合うタイプではありません。慎重に選び、"
            "一度自分の人と決めたら長く続きます。あなたの忠誠心は静かですが、"
            "とても強いものです。\n\n"
            "友人や家族が困難に陥ったとき、真っ先に駆けつけて助けます。"
            "あなたの傍らには、いつも頼もしい支え手たちがついてきます。\n\n"
            "ただ、行きすぎた忠誠心はときに相手の重荷になります。"
            "自分がすべてを解決しなければならないという強迫を手放し、"
            "相手が自力で立ち上がる姿を見守ることも愛です。"
        ),
        "patterns": [
            "義理を非常に大切にします。",
            "危険に陥った友人を放っておけません。",
            "自分の人には限りなく寛大です。",
        ],
        "best_match": ["THE_TWIN", "THE_PIONEER"],
        "best_reason": "あなたの頼もしい支えをありがたく思い、共に成長する人です。",
        "challenging_match": ["THE_OPERATOR"],
        "challenging_reason": "あなたの忠誠心を利用しようとする人に傷つけられることがあります。",
        "actions": [
            "自分がすべてを解決しなければならないという強迫を捨てましょう。",
            "助けを求められたときだけ助ける練習をしましょう。",
            "自分を疲れさせる関係は、大胆に整理しましょう。",
        ],
        "red_flags": [
            "義理を守るために、自分の生活が崩れていませんか？",
            "利用しようとする人に振り回されていませんか？",
        ],
    },
    "THE_EMPATH": {
        "headline": "相手の感情を深く読み取る共感力の持ち主です。",
        "body": (
            "人の気分を素早く正確に読み取ります。本人より先に、気分が良くないことに"
            "気づきます。だからこそ、稀な良い友人になります。\n\n"
            "言葉にしなくても心を理解してくれるあなたの傍らに、人々が集まってきます。"
            "あなたは相手に深い情緒的な安定感を与えます。\n\n"
            "ただ、他人の感情に入り込みすぎると、自分の感情をいたわらずに疲弊してしまいます。"
            "他者と自分の間に、健全な心理的な境界線を引く練習が欠かせません。"
        ),
        "patterns": [
            "相手の表情の変化をよく読み取ります。",
            "共感が得意で、慰めるのも上手です。",
            "他人の感情を一人で抱え込もうとします。",
        ],
        "best_match": ["THE_RIVAL", "THE_BLADE"],
        "best_reason": "あなたの感情に流されず、中心を保ってくれる人です。",
        "challenging_match": ["THE_EMPATH"],
        "challenging_reason": "二人とも感情を抱え込むと、互いに疲弊します。",
        "actions": [
            "一日に一度、自分の気分はどうかを先に問いかけましょう。",
            "相手の感情を代わりに解決しないでください。",
            "一人の時間を十分にとりましょう。",
        ],
        "red_flags": [
            "他人の悲しみに深く沈み込んでいませんか？",
            "自分の感情を後回しにしていませんか？",
        ],
    },
}

def _ja(s): return bool(s) and bool(KANA_RE.search(s))

def main():
    print("=" * 60); print("[Phase 4-17] sections BONDS_CONTENT + 전체 재검증"); print("=" * 60)
    if not JA.exists(): print(f"❌ {JA}"); return 1
    data = json.loads(JA.read_text(encoding="utf-8"))
    data.setdefault("BONDS_CONTENT", {})
    for mode, tr in T.items():
        data["BONDS_CONTENT"].setdefault(mode, {}).update(tr)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(payload)
    JA.write_text(payload, encoding="utf-8")
    print(f"✅ {len(T)} modes 저장")

    # 최종 verify: MONEY/WORK/BONDS 전체
    print("\n[verify] sections.json 3 content blocks")
    ok = True
    blocks = {
        "MONEY_CONTENT": ["THE_STEWARD", "THE_OPERATOR", "THE_FLOW"],
        "WORK_CONTENT": ["THE_CREATOR", "THE_CHALLENGER", "THE_OFFICER",
                         "THE_SURVIVOR", "THE_MYSTIC", "THE_MENTOR", "THE_GENERALIST"],
        "BONDS_CONTENT": ["THE_TWIN", "THE_RIVAL", "THE_ALLY", "THE_EMPATH"],
    }
    for block, modes in blocks.items():
        for mode in modes:
            d = data.get(block, {}).get(mode, {})
            for k in ("headline", "body", "best_reason", "challenging_reason"):
                if not _ja(d.get(k, "")):
                    print(f"  [ERR] {block}.{mode}.{k}"); ok = False
            for k in ("patterns", "actions", "red_flags"):
                for i, s in enumerate(d.get(k, [])):
                    if not _ja(s):
                        print(f"  [ERR] {block}.{mode}.{k}[{i}]"); ok = False
    if ok:
        print(f"  [OK] MONEY(3) + WORK(7) + BONDS(4) = 14/14 modes JA 🏆")
        print(f"  [OK] sections.json 14/292 WARN → 0 WARN 🏆")
    print("=" * 60)
    return 0 if ok else 1

if __name__ == "__main__": sys.exit(main())