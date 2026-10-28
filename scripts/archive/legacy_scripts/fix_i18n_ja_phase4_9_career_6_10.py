#!/usr/bin/env python3
"""Phase 4-9: JA career.json — archetypes 6-10 + SECTION_TITLE. career 100%."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
JA = ROOT / "app" / "services" / "content" / "data" / "ja" / "career.json"
KANA_RE = re.compile(r'[\u3040-\u30FF]')

T = {
    "THE_CULTIVATOR": {
        "headline": "教育・企画・人事など、人を育てる仕事に適しています。",
        "body": "あなたは人の可能性を見抜き、育てることに卓越しています。後輩を育成したり、プロジェクトを調整する役割がよく合います。\n\nこの気質は教育、人事、コンサルティング、企画で輝きます。逆に、成果だけを求める冷たい組織では消耗します。\n\nあなたのリスクは、成果を他人に譲ってしまうことです。自分の貢献を明確に記録し、アピールしましょう。",
        "patterns": ["後輩や同僚の成長に大きな関心があります。", "チームの雰囲気を柔らかくします。", "自分の実績を低く評価しがちです。"],
        "best_reason": "あなたの貢献を認め、共に成長してくれる人です。",
        "challenging_reason": "成果主義の人とは価値観の衝突が起きます。",
        "actions": ["月に一度、あなたの貢献を文書でまとめましょう。", "上司にキャリア目標を明確に伝えましょう。", "意識的にひとりのメンティーを育てましょう。"],
        "red_flags": ["あなたの実績を他人が持っていっていませんか？", "自分の成長を後回しにしていませんか？"],
    },
    "THE_BLADE": {
        "headline": "法曹・金融・軍警・エンジニアリングなど、原則が重要な場に合います。",
        "body": "あなたは論理的で、決断が速い。明確な基準と原則のある環境で最高の成果を出します。\n\nこの強みは法曹、金融、軍警、エンジニアリング、医療で輝きます。逆に、基準が曖昧な組織ではもどかしさを感じます。\n\nあなたのリスクは、人よりも原則を優先してしまうことです。結果は正しくても、関係が損なわれることがあります。柔らかなコミュニケーションが必要です。",
        "patterns": ["素早く結論を出します。", "論理的な抜け穴を見つけるのが得意です。", "感情的なコミュニケーションが苦手です。"],
        "best_reason": "あなたの鋭さを柔らかく包み込んでくれる人です。",
        "challenging_reason": "強い対立構図が繰り返され、チームが疲弊します。",
        "actions": ["結論の前に一度、感情を確認しましょう。", "月に一度、上司や同僚と非公式な会話を持ちましょう。", "自分の判断を柔らかく表現する練習をしましょう。"],
        "red_flags": ["「自分が正しい」という確信が関係を傷つけていませんか？", "同僚があなたに話しかけるのをためらっていませんか？"],
    },
    "THE_GEM": {
        "headline": "デザイン・アート・精密技術分野で頭角を現します。",
        "body": "あなたは完璧を追求します。細部へのこだわりがあなたの専門性を作り出します。\n\nこの気質はデザイン、アート、編集、精密加工、プレミアムサービスで輝きます。逆に、「速く、雑に」を求める組織では疲弊します。\n\nあなたのリスクは完璧主義で仕上がらないことです。80%で世に出す練習が必要です。",
        "patterns": ["細部にこだわります。", "完璧でないと世に出せません。", "低品質な成果物にストレスを感じます。"],
        "best_reason": "あなたの完璧主義を理解し、忍耐してくれる人です。",
        "challenging_reason": "速度優先主義の人とは方法が正面衝突します。",
        "actions": ["「これで十分」を実践しましょう。", "完璧なプロジェクトをひとつ選び、80%で公開しましょう。", "自分の基準を上司と事前に合意しましょう。"],
        "red_flags": ["完璧さのせいでスケジュールを逃していませんか？", "あなたの基準をチームに押し付けていませんか？"],
    },
    "THE_DEEP": {
        "headline": "戦略立案・分析・研究分野で卓越しています。",
        "body": "あなたは大きな絵を描く能力に優れています。表面の下の構造を見抜く力があります。\n\nこの気質は戦略立案、リサーチ、コンサルティング、データ分析で輝きます。逆に、実行だけを求める立場ではもどかしさを感じます。\n\nあなたのリスクは分析に没頭して実行が遅れることです。実行力の強いパートナーと組むことで、シナジーが最大化します。",
        "patterns": ["まず大きな絵を描きます。", "実行の前に分析に時間をかけます。", "表面的な仕事を嫌います。"],
        "best_reason": "あなたの戦略を実行に移してくれる人です。",
        "challenging_reason": "素早い実行を求める人と衝突することがあります。",
        "actions": ["戦略化から3日以内に最初の実行を始めましょう。", "実行力の強いパートナーを見つけましょう。", "分析に30%の時間制限を設けましょう。"],
        "red_flags": ["分析ばかりで実行を先延ばしにしていませんか？", "決断のタイミングを逃していませんか？"],
    },
    "THE_SPRING": {
        "headline": "静かにチームを支え、信頼を築きます。",
        "body": "あなたは派手ではありませんが、なくてはならない中核人材です。チームの衝突を溶かし、静かに問題を解決します。\n\nこの強みはオペレーション、人事、カスタマーサポート、プロジェクトマネジメントで輝きます。逆に、自己PRが重視される営業組織では過小評価されます。\n\nあなたのリスクは実績が認められないことです。自分の貢献を積極的にアピールする練習が必要です。",
        "patterns": ["チームの静かな問題解決者です。", "自分の実績をうまく見せません。", "衝突の調停が得意です。"],
        "best_reason": "あなたの静かな支えを認め、引き上げてくれる人です。",
        "challenging_reason": "派手な成果だけが注目される組織では存在感が消えます。",
        "actions": ["月に一度、実績を文書に残しましょう。", "会議で一度は自分の貢献について発言しましょう。", "あなたを認めてくれる上司を見つけましょう。"],
        "red_flags": ["あなたの実績が他人のものとして記録されていませんか？", "静かさのせいで無視されていませんか？"],
    },
}

SECTION_TITLE = "キャリアと転機"

def _ja(s): return bool(s) and bool(KANA_RE.search(s))

def main():
    print("=" * 60); print("[Phase 4-9] career 6-10 + SECTION_TITLE"); print("=" * 60)
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
    if ok and all_ok: print("  [OK] career.json 100% JA (10/10) 🏆")
    print("=" * 60)
    return 0 if (ok and all_ok) else 1

if __name__ == "__main__": sys.exit(main())