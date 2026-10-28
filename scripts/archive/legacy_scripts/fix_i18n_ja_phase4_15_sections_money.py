#!/usr/bin/env python3
"""Phase 4-15: JA sections.json — MONEY_CONTENT 3 modes."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
JA = ROOT / "app" / "services" / "content" / "data" / "ja" / "sections.json"
KANA_RE = re.compile(r'[\u3040-\u30FF]')

T = {
    "THE_STEWARD": {
        "headline": "資産を安全に守り、複利で育てていきます。",
        "body": (
            "あなたはリスクを極端に嫌い、元本割れに耐えられません。"
            "目の前の短期リターンより、長期的な安定性を最優先に考えます。\n\n"
            "そうした気質は、預貯金・債券・不動産といった確実な安全資産を好む方向へと導きます。"
            "他の人が暗号通貨やデイトレードに熱狂しているとき、あなたは静かに資産を守り、育てます。\n\n"
            "ただ、過度な保守性はインフレに勝てない結果を招きます。"
            "資産の一部は成長資産にも分散投資する知恵が必要です。"
        ),
        "patterns": [
            "現金と預貯金の比率が非常に高いです。",
            "損失への恐れが大きく、決定を先延ばしにします。",
            "複利の力を信じ、長期保有を好みます。",
        ],
        "best_match": ["THE_OPERATOR", "THE_FLOW"],
        "best_reason": "あなたの安全資産の上にリターンを乗せてくれるパートナーです。",
        "challenging_match": ["THE_STEWARD"],
        "challenging_reason": "二人とも安全だけを求めると、資産が物価上昇率に追いつけません。",
        "actions": [
            "資産の10%だけをインデックスファンドに分散投資しましょう。",
            "年に1回、預金金利と物価上昇率を比較しましょう。",
            "自動積立で積立投資を始めましょう。",
        ],
        "red_flags": [
            "すべての財産が預金だけに縛られていませんか？",
            "知人にお金を貸して返ってこなかったことはありませんか？",
        ],
    },
    "THE_OPERATOR": {
        "headline": "流動的な資産運用と機会の捕捉に卓越しています。",
        "body": (
            "あなたはお金が流れることを楽しみます。資本を寝かせるより、"
            "新たな機会を捉えて回すことに長けています。\n\n"
            "副業・小規模事業・短期投資など、多方面で収益を生み出す感覚があります。"
            "速い決断力のおかげで、他の人がためらうとき大胆に賭け、大きなリターンを得ることもあります。\n\n"
            "ただ、すべての流れが速くなると、漏れる穴もまた大きくなります。"
            "キャッシュフローが良いときにセーフティネットを確保しなければ、危機に脆くなります。"
        ),
        "patterns": [
            "多様な収入源を作ろうとします。",
            "リスクを取るが、リスクを分散させます。",
            "支出も収入と同じくらい速く発生します。",
        ],
        "best_match": ["THE_STEWARD", "THE_ANCHOR"],
        "best_reason": "あなたがばらまいた資産を堅固に守ってくれるパートナーです。",
        "challenging_match": ["THE_OPERATOR"],
        "challenging_reason": "二人ともリスクを楽しむと、危機のときの回復が難しくなります。",
        "actions": [
            "収入の30%は必ず自動貯蓄に固定しましょう。",
            "新しい投資の前に3日間の熟慮期間を置きましょう。",
            "クレジットカードではなくデビットカードを使って支出を統制しましょう。",
        ],
        "red_flags": [
            "収入は多いのに口座に何も残っていませんか？",
            "借金をして投資していませんか？",
        ],
    },
    "THE_FLOW": {
        "headline": "状況に合わせて柔軟にお金の流れに乗ります。",
        "body": (
            "あなたはお金に対する固定観念がありません。人脈・直感・そして状況の流れに乗って、"
            "自然に収入を作り出します。\n\n"
            "あるときは大きなお金が入り、あるときは空っぽになります。"
            "それでもその流れを淡々と受け止め、必要な瞬間に機会を引き寄せる力があります。\n\n"
            "そうした柔軟さは強みですが、計画なく即興的に支出する癖は財政を危うくします。"
            "最低限のセーフティネットは不可欠です。"
        ),
        "patterns": [
            "収入と支出の起伏が大きいです。",
            "人を通じて財の機会を得ます。",
            "予算を組むよりも、そのときどきで使います。",
        ],
        "best_match": ["THE_STEWARD", "THE_ANCHOR"],
        "best_reason": "あなたが起伏のない人生を送れるよう、中心を取ってくれる人です。",
        "challenging_match": ["THE_OPERATOR"],
        "challenging_reason": "二人とも即興的だと破産への近道です。",
        "actions": [
            "口座を二つに分けましょう（緊急費／生活費）。",
            "大きな支出の前には必ず24時間待ちましょう。",
            "毎月の収入の10%は無条件で貯蓄しましょう。",
        ],
        "red_flags": [
            "カードの支払いを回し払いにしていませんか？",
            "知人の誘いで投資して損をしたことはありませんか？",
        ],
    },
}

def _ja(s): return bool(s) and bool(KANA_RE.search(s))

def main():
    print("=" * 60); print("[Phase 4-15] sections MONEY_CONTENT"); print("=" * 60)
    if not JA.exists(): print(f"❌ {JA}"); return 1
    data = json.loads(JA.read_text(encoding="utf-8"))
    data.setdefault("MONEY_CONTENT", {})
    for mode, tr in T.items():
        data["MONEY_CONTENT"].setdefault(mode, {}).update(tr)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(payload)
    JA.write_text(payload, encoding="utf-8")
    print(f"✅ {len(T)} modes 저장")
    print("\n[verify]")
    ok = True
    for mode in T:
        d = data["MONEY_CONTENT"][mode]
        for k in ("headline", "body", "best_reason", "challenging_reason"):
            if not _ja(d.get(k, "")): print(f"  [ERR] {mode}.{k}"); ok = False
        for k in ("patterns", "actions", "red_flags"):
            for i, s in enumerate(d.get(k, [])):
                if not _ja(s): print(f"  [ERR] {mode}.{k}[{i}]"); ok = False
    if ok: print("  [OK] MONEY_CONTENT 3/3 = JA")
    print("=" * 60)
    return 0 if ok else 1

if __name__ == "__main__": sys.exit(main())