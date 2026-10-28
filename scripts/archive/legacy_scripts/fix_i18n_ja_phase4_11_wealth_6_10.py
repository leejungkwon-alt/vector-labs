#!/usr/bin/env python3
"""Phase 4-11: JA wealth.json — archetypes 6-10 + SECTION_TITLE. wealth 100%."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
JA = ROOT / "app" / "services" / "content" / "data" / "ja" / "wealth.json"
KANA_RE = re.compile(r'[\u3040-\u30FF]')

T = {
    "THE_CULTIVATOR": {
        "headline": "誠実な労働と着実な積立が富を築きます。",
        "body": "あなたは幸運を信じません。忠実な貯蓄と複利の力を信じます。\n\nこの気質は積立投資、年金、長期預金で輝きます。逆に、投機的な投資には絶対に手を出さないでください。\n\nあなたのリスクは知人にお金を貸すことです。お金を貸せば関係も失います。",
        "patterns": ["着実に貯蓄します。", "複利の力を信じます。", "知人の頼みに弱い。"],
        "best_reason": "あなたの誠実さを理解し、共に成長する人です。",
        "challenging_reason": "素早いリターンを望む人と衝突します。",
        "actions": ["毎月自動振込で積立投資をしましょう。", "知人にお金を貸さないようにしましょう。", "年金貯蓄に加入しましょう。"],
        "red_flags": ["知人にお金を貸して返ってこなかったことは？", "積立投資を先延ばしにしていませんか？"],
    },
    "THE_BLADE": {
        "headline": "決断力ある投資で利益を出します。",
        "body": "あなたは損切りと利確が速い。市場の流れを論理的に分析して決断を下します。\n\nこの気質は株式、先物、トレーディングで輝きます。逆に、感情的な投資や仮想通貨には危険です。\n\nあなたのリスクはレバレッジ（借金投資）です。大きな利益の後に大きな損失が来ます。レバレッジは絶対に禁止です。",
        "patterns": ["損切りと利確が速い。", "論理的に市場を分析します。", "自分の判断に強い確信を持ちます。"],
        "best_reason": "あなたのリスクをコントロールしてくれる人です。",
        "challenging_reason": "二人とも攻撃的だと、危機のときの回復が難しくなります。",
        "actions": ["レバレッジは絶対に使いません。", "ポートフォリオの70%は安全資産に置きましょう。", "売買日誌を書きましょう。"],
        "red_flags": ["借金投資で大きな損失を出したことは？", "感情的な売買をしていませんか？"],
    },
    "THE_GEM": {
        "headline": "価値ある物・希少資産に投資しましょう。",
        "body": "あなたは美しさと希少性への感覚が優れています。高級品、芸術品、高級不動産などで財運が開きます。\n\nこの気質は美術品、時計、ワイン、プレミアム不動産投資に適しています。逆に、低価格株のデイトレードには向きません。\n\nあなたのリスクは趣味と投資を混同することです。感情的な消費と投資を分けましょう。",
        "patterns": ["美しさに投資します。", "希少性に敏感です。", "感情的な消費が多い。"],
        "best_reason": "あなたの趣味を理解し、財務を管理してくれる人です。",
        "challenging_reason": "二人とも感情的な消費が激しければ破産します。",
        "actions": ["趣味の予算と投資の予算を分けましょう。", "美術品や時計は専門家の鑑定を経ましょう。", "感情的な消費は24時間後に決めましょう。"],
        "red_flags": ["「これは投資だ」と言いながら消費していませんか？", "感情で売買していませんか？"],
    },
    "THE_DEEP": {
        "headline": "他人が知らないときに買い、知ったときに売る戦略家です。",
        "body": "あなたは市場の構造を分析します。大衆が興奮しているときに静かに、恐怖に陥っているときに大胆に動きます。\n\nこの気質はバリュー投資、長期投資、非上場株、不動産で輝きます。\n\nあなたのリスクは分析に没頭してタイミングを逃すことです。決断の期限を定めましょう。",
        "patterns": ["市場の構造を分析します。", "逆張り投資を好みます。", "決断に時間がかかります。"],
        "best_reason": "あなたの分析を実行に移してくれる人です。",
        "challenging_reason": "二人とも分析だけなら機会を逃します。",
        "actions": ["決断の期限を定めましょう。", "分析は3日以内に終えましょう。", "実行パートナーを見つけましょう。"],
        "red_flags": ["分析するうちに機会を逃したことは？", "決断を先延ばしにし続けていませんか？"],
    },
    "THE_SPRING": {
        "headline": "直感を信じ、柔軟に対処します。",
        "body": "あなたはお金の流れを本能的に読みます。他人には見えない機会を感じ取る力があります。\n\nこの気質は短期投資、トレーディング、ビジネス機会の捕捉で輝きます。\n\nあなたのリスクは周囲の人の誘いに乗ってしまうことです。確信がなければ、きっぱりと断りましょう。",
        "patterns": ["直感で機会を捉えます。", "柔軟に対処します。", "周囲の誘いに弱い。"],
        "best_reason": "あなたの直感を検証してくれる人です。",
        "challenging_reason": "二人とも衝動的なら危機のときに崩れます。",
        "actions": ["大きな投資の前に必ず専門家の検証を受けましょう。", "知人の投資勧誘は3日後に決めましょう。", "収入の10%は自動貯蓄しましょう。"],
        "red_flags": ["周囲の誘いに乗って損をしたことは？", "直感だけを信じて検証を省いていませんか？"],
    },
}

SECTION_TITLE = "富と投資"

def _ja(s): return bool(s) and bool(KANA_RE.search(s))

def main():
    print("=" * 60); print("[Phase 4-11] wealth 6-10 + SECTION_TITLE"); print("=" * 60)
    if not JA.exists(): print(f"❌ {JA}"); return 1
    data = json.loads(JA.read_text(encoding="utf-8"))
    data["SECTION_TITLE"] = SECTION_TITLE
    for arch, tr in T.items():
        data.setdefault("CONTENT", {}).setdefault(arch, {}).update(tr)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(payload)
    JA.write_text(payload, encoding="utf-8")
    print(f"✅ SECTION_TITLE + {len(T)}개 저장")
    print("\n[verify]")
    ok = True
    for arch, tr in T.items():
        d = data["CONTENT"][arch]
        for k in ("headline", "body", "best_reason", "challenging_reason"):
            if not _ja(d.get(k, "")): print(f"  [ERR] {arch}.{k}"); ok = False
        for k in ("patterns", "actions", "red_flags"):
            for i, s in enumerate(d.get(k, [])):
                if not _ja(s): print(f"  [ERR] {arch}.{k}[{i}]"); ok = False
    all_ok = True
    for arch, d in data.get("CONTENT", {}).items():
        if not _ja(d.get("headline", "")): print(f"  [잔여EN] {arch}"); all_ok = False
    if ok and all_ok:
        print("  [OK] wealth.json 100% JA (10/10) 🏆")
        # 3대장 종합 체크
        print("\n[종합]")
        import json as _j
        base = ROOT / "app" / "services" / "content" / "data" / "ja"
        trio = {}
        for f in ("love", "career", "wealth"):
            d = _j.loads((base / f"{f}.json").read_text(encoding="utf-8"))
            n = sum(1 for a, v in d.get("CONTENT", {}).items() if _ja(v.get("headline", "")))
            trio[f] = f"{n}/10"
        print(f"  love={trio['love']}  career={trio['career']}  wealth={trio['wealth']} 🏆")
    print("=" * 60)
    return 0 if (ok and all_ok) else 1

if __name__ == "__main__": sys.exit(main())