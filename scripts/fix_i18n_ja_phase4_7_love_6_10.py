#!/usr/bin/env python3
"""Phase 4-7: JA love.json — archetypes 6-10 + SECTION_TITLE. love 100%."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
JA = ROOT / "app" / "services" / "content" / "data" / "ja" / "love.json"
KANA_RE = re.compile(r'[\u3040-\u30FF]')

T = {
    "THE_CULTIVATOR": {
        "headline": "相手を丁寧に気遣う恋愛をします。",
        "body": "あなたは相手の必要を敏感に読み取ります。深い配慮を持ち、相手が快適に感じる環境を作るのが得意です。\n\nしかし、この気遣いが過剰になれば、相手は無力になります。「私が何でもやってあげる」という態度は、相手の成長の機会を奪いかねません。\n\nあなたの愛は庭仕事のようなものです。植物が自ら育つように水と光だけを与えるほうが、無理に育てるより長く続きます。",
        "patterns": ["相手が必要とする前に世話をします。", "相手の問題を代わりに解決しようとします。", "相手が感謝を示さないと失望を感じます。"],
        "best_reason": "互いの気遣いの方法を理解し、その中で心地よく感じられます。",
        "challenging_reason": "表現が華やかな人とでは、あなたの静かな献身が十分に見られないことがあります。",
        "actions": ["相手が失敗しても、一度は介入せずに見守りましょう。", "頼まれたときだけ気遣いを提供する練習をしましょう。", "自分のための時間を確保しましょう。"],
        "red_flags": ["過剰な気遣いで相手の自立を妨げていませんか？", "相手があなたの献身を当然と思っていませんか？"],
    },
    "THE_BLADE": {
        "headline": "誠実でまっすぐな恋愛をします。",
        "body": "あなたは嘘が嫌いです。曖昧な関係や表面的な表現よりも、はっきりした感情を好みます。\n\nこのまっすぐさは信頼を与えますが、ときに相手の感情を傷つけます。正しい言葉も、タイミングと方法を誤れば傷になります。\n\nあなたの本当の強みは「相手が必要とするときに、必要なことを正確に言う」力です。この力を温もりで包めば、関係ははるかに深まります。",
        "patterns": ["問題を指摘し、すぐに解決しようとします。", "曖昧さに耐えられません。", "感情よりも論理で会話を導きます。"],
        "best_reason": "あなたの誠実さを柔らかく包み、あなたが見落とす感情を読み取ってくれる人です。",
        "challenging_reason": "二人とも強く押せば、会話が喧嘩になります。",
        "actions": ["指摘する前に、まず相手の立場を尋ねましょう。", "答えを出す前に質問をしましょう。", "あなたの感情も言葉で表現してみましょう。"],
        "red_flags": ["正しいからという理由で相手を追い詰めていませんか？", "あなたの直接さが相手に脅威と感じられていませんか？"],
    },
    "THE_GEM": {
        "headline": "理想が高く、こだわりの強い恋愛をします。",
        "body": "あなたは簡単に妥協しません。相手の趣味、話し方、態度をひとつひとつ注意深く観察します。\n\nこの几帳面さは関係の質を高めますが、相手にとっては負担になることがあります。「なぜ自分はいつも足りないのか」と感じさせれば、愛は重くなります。\n\nあなたの基準は贈り物です。しかし、それを相手に押し付けなければ、関係は二人のためのものへと育ちます。",
        "patterns": ["相手の小さな欠点を長く覚えています。", "完璧な瞬間を待つうちにタイミングを逃します。", "関係の完璧さを頻繁に確認します。"],
        "best_reason": "深さと忍耐を持つ人が、負担なくあなたの基準を受け止めます。",
        "challenging_reason": "二人とも完璧を求めれば、何も十分にはなりません。",
        "actions": ["80%満足できたら「これで十分」と言いましょう。", "毎週、相手の欠点をひとつ認めて手放しましょう。", "自分にも寛大でいましょう。"],
        "red_flags": ["「これで十分」と言えずにいませんか？", "相手があなたの前で緊張していませんか？"],
    },
    "THE_DEEP": {
        "headline": "深く慎重な恋愛をします。",
        "body": "あなたは感情を簡単には明かしません。相手を十分に観察し、心を決めたら深く掘り下げます。\n\nこの慎重さは成熟した愛のように見えますが、相手があなたの本当の感情を知るのは難しいものです。「この人は私を好きなのか」という問いが関係を遠ざけます。\n\nあなたの愛は海のようなものです。表面は穏やかですが、ときに水面へ上がって「私はここにいる」と相手に知らせる必要があります。",
        "patterns": ["感情を分析し整理してから表現します。", "相手を長く観察し、ゆっくり近づきます。", "本心を明かすのが遅く、相手をじらします。"],
        "best_reason": "深さを理解する人が、あなたのゆっくりした愛を待ってくれます。",
        "challenging_reason": "素早い感情表現を望む人とはペースが合わないかもしれません。",
        "actions": ["感情を分析せず、ただ言葉にしましょう。", "一日に一度、心を一文で表現しましょう。", "相手にあなたのペースを理解させましょう。"],
        "red_flags": ["分析するうちにタイミングを逃していませんか？", "相手があなたの心を知る機会を与えていますか？"],
    },
    "THE_SPRING": {
        "headline": "静かで愛情深い恋愛をします。",
        "body": "あなたは相手を心地よくさせる力を持っています。誇張なく、自然に相手の一日に沁み込んでいきます。\n\nしかし、この静けさが過剰になれば、相手はあなたの感情を知るのが難しくなります。「この人は私を好きなのか」という問いが関係を遅らせます。\n\nあなたの愛情は強い。しかし、その愛情をときどき明確な言葉で表現すれば、関係はより深まります。",
        "patterns": ["言葉よりも雰囲気で愛を伝えます。", "相手の気分によく合わせます。", "感情表現が遅く、機会を逃すことがあります。"],
        "best_reason": "はっきりした人があなたの静かな心を引き出します。",
        "challenging_reason": "二人とも静かだと、感情が永遠に明かされないかもしれません。",
        "actions": ["好きだと直接言いましょう。", "週に一度、相手への気持ちを表現しましょう。", "あなたのペースを相手に伝えましょう。"],
        "red_flags": ["「いつか分かってくれる」と思って先延ばしにしていませんか？", "相手があなたの気持ちを疑っていませんか？"],
    },
}

SECTION_TITLE = "恋愛と結婚"

def _ja(s): return bool(s) and bool(KANA_RE.search(s))

def main():
    print("=" * 60); print("[Phase 4-7] love 6-10 + SECTION_TITLE"); print("=" * 60)
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
    # 전체 love.json JA 커버리지 재확인
    all_ok = True
    for arch, d in data.get("CONTENT", {}).items():
        if not _ja(d.get("headline", "")): print(f"  [잔여EN] {arch}"); all_ok = False
    if ok and all_ok: print("  [OK] love.json 100% JA (10/10) 🏆")
    print("=" * 60)
    return 0 if (ok and all_ok) else 1

if __name__ == "__main__": sys.exit(main())