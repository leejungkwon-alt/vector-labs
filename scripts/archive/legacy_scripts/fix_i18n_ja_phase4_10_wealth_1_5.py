#!/usr/bin/env python3
"""Phase 4-10: JA wealth.json — archetypes 1-5."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
JA = ROOT / "app" / "services" / "content" / "data" / "ja" / "wealth.json"
KANA_RE = re.compile(r'[\u3040-\u30FF]')

T = {
    "THE_PIONEER": {
        "headline": "ビジネスを通じた資産成長が合っています。",
        "body": "あなたは自分のアイデアでお金を稼ぐ能力があります。他人が作ったシステムに投資するよりも、自分で盤面を作るほうが合っています。\n\nこの気質は起業、新規事業、個人ブランドで輝きます。逆に、単純なデイトレードは性格に合いません。\n\nあなたのリスクは、すべてを一度に賭けたい衝動です。大きな賭けの前に、安定したキャッシュフローを作りましょう。",
        "patterns": ["アイデアでお金を稼ぎます。", "大きな賭けを楽しみます。", "着実な管理が苦手です。"],
        "best_reason": "あなたが稼いだお金を守ってくれる人です。",
        "challenging_reason": "二人ともリスクを楽しむと、危機のときの回復が難しくなります。",
        "actions": ["収入の30%は自動貯蓄で固定しましょう。", "一度に大きな賭けをする代わりに3ヶ月分割で投資しましょう。", "財務マネージャーを置きましょう。"],
        "red_flags": ["稼いだお金がどこに消えたか分からないのでは？", "生活費の口座が空になっていませんか？"],
    },
    "THE_ADAPTER": {
        "headline": "多様な収入源を持つときに財運が開きます。",
        "body": "あなたは一箇所に集中するとリスクが大きくなります。複数の井戸を掘ることがあなたの財産戦略です。\n\nこの気質は副業、フリーランス、複数の収入源、小規模投資に適しています。逆に、一社・一資産に全財産を賭けるのは危険です。\n\nあなたのリスクは、稼ぐけれど貯まらないことです。自動貯蓄をひとつだけ確実に行いましょう。",
        "patterns": ["複数の収入源を作るのが得意です。", "支出も柔軟です。", "一箇所に集中するのが苦手です。"],
        "best_reason": "あなたの散らばった収入をまとめてくれる人です。",
        "challenging_reason": "二人とも散らばると財務管理が立ち行かなくなります。",
        "actions": ["自動貯蓄口座をひとつ作りましょう。", "月ごとの収支表を作りましょう。", "主収入源のひとつに専門性を加えましょう。"],
        "red_flags": ["収入は多いのに貯蓄がゼロでは？", "複数の収入源にエネルギーが分散していませんか？"],
    },
    "THE_RADIATOR": {
        "headline": "名誉と富が共にやってくるタイプです。",
        "body": "あなたは人を通じてお金を稼ぎます。人脈、評判、ブランドがあなたの資産です。\n\nこの気質は事業、営業、エンターテインメントで輝きます。逆に、孤独な分析投資は苦手です。\n\nあなたのリスクは、使うときに大きく使うことです。自動貯蓄と支出上限の設定が必須です。",
        "patterns": ["人を通じて機会を得ます。", "使うときも大きく使います。", "衝動買いが多い。"],
        "best_reason": "あなたの支出を節制してくれる人です。",
        "challenging_reason": "二人とも大きく使えば破産します。",
        "actions": ["収入の20%は自動振込で貯蓄しましょう。", "月の支出上限を決めましょう。", "大きな出費は24時間後に決めましょう。"],
        "red_flags": ["カード請求が収入を超えていませんか？", "衝動買いの後悔が多いのでは？"],
    },
    "THE_KEEPER": {
        "headline": "資産を守り育てることに卓越しています。",
        "body": "あなたはリスクを極度に嫌います。安全資産を好み、元本割れに耐えられません。\n\nこの気質は預貯金、債券、不動産など安定資産で輝きます。逆に、デイトレードや仮想通貨には絶対に手を出さないでください。\n\nあなたのリスクは物価上昇に勝てないことです。適切な水準のインフレヘッジ投資が必要です。",
        "patterns": ["安全資産を好みます。", "元本損失に敏感です。", "着実に貯めます。"],
        "best_reason": "あなたの安全資産の上にリターンを乗せてくれる人です。",
        "challenging_reason": "リスク選好が正反対で、財務的な衝突が生じます。",
        "actions": ["資産の10%だけをインデックスファンドに投資しましょう。", "物価上昇率と預金金利を比較しましょう。", "年に一度財務点検を行いましょう。"],
        "red_flags": ["すべての財産が預金だけに縛られていませんか？", "物価上昇率に追いつけていませんか？"],
    },
    "THE_ANCHOR": {
        "headline": "不動産などの実物資産で財運を見出します。",
        "body": "あなたは目に見える実物資産に強い。不動産、金、預貯金など手に取れる資産で財運が開きます。\n\nこの気質は長期投資、不動産、実物資産に適しています。逆に、仮想通貨やデリバティブには向きません。\n\nあなたのリスクは機会を逃すことです。安全だけを求めすぎれば、資産は成長しません。",
        "patterns": ["実物資産を好みます。", "長期投資に強い。", "素早い機会の捕捉は苦手です。"],
        "best_reason": "あなたの安定資産を調整してくれる人です。",
        "challenging_reason": "素早い賭けを望む人と衝突します。",
        "actions": ["資産の20%を成長資産に配分しましょう。", "不動産以外の代替投資を学びましょう。", "年に一度ポートフォリオをリバランスしましょう。"],
        "red_flags": ["すべての資産が不動産に集中していませんか？", "新しい投資機会を無視していませんか？"],
    },
}

def _ja(s): return bool(s) and bool(KANA_RE.search(s))

def main():
    print("=" * 60); print("[Phase 4-10] wealth 1-5"); print("=" * 60)
    if not JA.exists(): print(f"❌ {JA}"); return 1
    data = json.loads(JA.read_text(encoding="utf-8"))
    for arch, tr in T.items():
        data.setdefault("CONTENT", {}).setdefault(arch, {}).update(tr)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(payload)
    JA.write_text(payload, encoding="utf-8")
    print(f"✅ {len(T)}개 저장")
    print("\n[verify]")
    ok = True
    for arch, tr in T.items():
        d = data["CONTENT"][arch]
        for k in ("headline", "body", "best_reason", "challenging_reason"):
            if not _ja(d.get(k, "")): print(f"  [ERR] {arch}.{k}"); ok = False
        for k in ("patterns", "actions", "red_flags"):
            for i, s in enumerate(d.get(k, [])):
                if not _ja(s): print(f"  [ERR] {arch}.{k}[{i}]"); ok = False
    if ok: print("  [OK] wealth 1-5 = JA (5/10)")
    print("=" * 60)
    return 0 if ok else 1

if __name__ == "__main__": sys.exit(main())