#!/usr/bin/env python3
"""
Phase 4-1: JA compatibility — ELEMENT_CONTENT (romance/business) + OVERALL + DISCLAIMER + RELATIONSHIP_CONTENT
- 기존 en 초안(짧은 영어)을 일본어 장문으로 전면 교체
- friend/family ELEMENT는 Phase 4-3 대상 (여기선 다루지 않음)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JA_COMPAT = ROOT / "app" / "services" / "content" / "data" / "ja" / "compatibility.json"
KANA_RE = re.compile(r'[\u3040-\u30FF]')

ELEMENT = {
    "romance": {
        "COMPLEMENTARY": {
            "headline": "二人の異なるエネルギーが恋の火花と情緒的な安らぎを灯す、調和のとれた愛です。",
            "body": "二人の元素エネルギーは自然な交響曲のように互いへと流れ込み、わくわくしつつも安心できる自然なつながりを生み出します。人生が一方のパートナーに疲れや感情の波をもたらすとき、もう一方は調和を取り戻すために必要な温もりや新鮮な視点を本能的に差し出します。自分を小さくする必要はありません。二人の自然な違いが、絆の最良の部分を引き出します。この有機的なシナジーは日ごとに絆を深め、本当に満たされる愛を築いていきます。",
        },
        "BALANCED": {
            "headline": "共有する内なるリズムと深い相互理解に根ざした、気楽な情緒の聖域です。",
            "body": "二人の基礎となるエネルギーの構成が似たベースを共有しているため、一緒にいることは慣れ親しんだ避難所に帰るように心地よく感じられます。感情の体験を驚くほど似たレンズで処理するため、長い説明や複雑な妥協はほとんど必要ありません。この自然な調和は穏やかで安全な環境を生み出し、二人とも偽りのない自分を完全に見てもらい、情緒的に安全だと感じます。時が経つにつれ、この平和なベースラインは人生の予期せぬ嵐を容易に乗り越える、壊れない情緒の基盤を形成します。",
        },
        "MODERATE": {
            "headline": "安心できる共通点と魅力的な違いの健康的なブレンドによって豊かになる、ダイナミックな恋愛です。",
            "body": "二人のエネルギー的なつながりは刺激的な中間地点を提供し、恋愛の安定とお互いへの尽きない好奇心が出会います。人生の大きな決断を滑らかに進めるのに十分な共通の価値観を持ちながらも、惹かれ合いを保つのに十分な個性を保ちます。このさりげない違いが関係を予測可能な日常に落とし込むのを防ぎ、パートナーの新しい側面を発見し続けることを促します。開かれた温かいコミュニケーションを保つ限り、あなた方の関係はより豊かで活気あるパートナーシップへと進化し続けます。",
        },
        "TENSION": {
            "headline": "エネルギー的なコントラストが激しい惹かれ合いと深い個人的成長を引き起こす、情熱的な関係です。",
            "body": "二人の対照的な元素エネルギーは強く帯電した磁気的な化学反応を生み出し、恋愛を活気に満ち、情熱的で、深く惹きつけるものに保ちます。感情的な状況を著しく異なる視点から見るため、ストレスレベルが高いときに誤解が生じることがあります。しかし、意識的な忍耐と優しさをもって接するとき、この摩擦の瞬間は情緒的な気づきを広げる強力な触媒として働きます。パートナー独自の感情の感じ方を受け入れることは、潜在的な衝突を、あなた方独自の絆の深遠な祝福へと変えるのです。",
        },
        "DEFAULT": {
            "headline": "相互の好奇心、穏やかな発見、無条件の尊重の上に築かれた、愛のための開かれたキャンバスです。",
            "body": "二人のエネルギーの相互作用は、意識的な意図と誠実な感謝を通じて愛が育つ、きれいで開かれた空間を提供します。固い仮定をせず、互いに期待を押し付けずに、相手の情緒世界を探検するよう招かれています。注意深く耳を傾け、パートナーがあなたの人生にもたらす独特な特質を祝うことによって、あなたは継続的な恋愛の再生の流れを解き放ちます。手に手を取って歩みながら、互いに成長する自由を与えることは、しなやかで深く愛に満ちたパートナーシップを築きます。",
        },
    },
    "business": {
        "COMPLEMENTARY": {
            "headline": "戦略的ビジョンと運営実行が完璧に噛み合い、高いシナジーを生み出すパートナーシップです。",
            "body": "二人の元素エネルギーはよく構造化された組織のように統合し、運営上の盲点を自然に補い、戦略的リスクをバランスさせます。一方が分析的疲労や市場の曖昧さに直面したとき、もう一方はプロジェクトを前進させるために必要な決断の勢いや安定の枠組みを本能的に提供します。成果のために自分の働き方を妥協する必要はなく、異なる機能的強みが複合的競争優位を解き放ちます。この自然なシナジーは長期的な商業的信頼を育み、持続可能な成長と卓越したビジネス成果を導きます。",
        },
        "BALANCED": {
            "headline": "共有する仕事のリズムと相互の戦略的明晰さに根ざした、摩擦のない運営の一致です。",
            "body": "二人の基礎となる仕事のスタイルが一貫したプロフェッショナルなベースラインを共有しているため、複雑な施策での協働は直感的で秩序正しく、極めて効率的に感じられます。リスクを評価し、優先順位を交渉し、ワークフローを構造化する方法が驚くほど似ているため、重要な意思決定の瞬間の摩擦を最小限に抑えます。この共有された運営の波長は信頼できる仕事環境を生み出し、両パートナーはマイクロマネジメントなしに高リスクのタスクを実行できます。時が経つにつれ、この安定したベースラインは市場の変動を乗り越えられる揺るがない組織的基盤を確立します。",
        },
        "MODERATE": {
            "headline": "共有の企業目標と補完的な問題解決アプローチで豊かになる、多才なビジネスダイナミクスです。",
            "body": "二人のプロフェッショナルなシナジーは、構造的な一致と問題解決の創造的多様性の間で実用的なバランスを取ります。長期的なロードマップを揃えるのに十分な共通のビジネス目標を共有しながらも、集団思考を防ぐのに十分な運営上の対照を保ちます。このさりげない違いは健全な社内議論を促し、提案を洗練させ、複雑な業界課題への革新的な解決策を発見させます。透明で客観的なコミュニケーションを維持することは、運営上の違いを明確な商業的優位へと絶えず変えていくでしょう。",
        },
        "TENSION": {
            "headline": "対照的な視点が鋭い革新と市場の機敏さを駆動する、高性能なビジネスパートナーシップです。",
            "body": "二人の対照的な元素エネルギーは、従来の考え方に挑み、戦略的反復を加速させる、高エネルギーな企業ダイナミクスを生み出します。リスク管理と実行を根本的に異なる視点から捉えるため、ピボットの局面では戦略をめぐる激しい議論が時折起きることがあります。しかし、プロフェッショナルな規律と相互の尊重をもって管理するとき、この緊張は徹底した品質管理と厳格な市場検証のための強力なエンジンとして機能します。パートナー独自の戦略的方法論を受け入れることは、運営上の摩擦を画期的な市場リーダーシップへと変えるのです。",
        },
        "DEFAULT": {
            "headline": "客観的分析、プロフェッショナルな尊重、明確な境界線の上に築かれた、協働のための多才な枠組みです。",
            "body": "二人のエネルギーダイナミクスは、意図的な構造と戦略的一致によって合弁事業が繁栄する、開かれ、非常に適応性の高いベースラインを提供します。互いに固い個人的な働き方を押し付け合うことなく、透明なガバナンスと明確な運営の境界線を確立できる立場にいます。開かれたコミュニケーションを維持し、パートナーがバランスシートにもたらす独自の価値を認めることで、しなやかな商業的同盟を育みます。各パートナーに自領域に対する専用の自律性を与えることは、持続可能なビジネス拡大のための強力で拡張可能な基盤を生み出します。",
        },
    },
}

OVERALL = {
    "PEAK": {"headline": "構造的に稀な適合です。",
             "body": "この組み合わせは四つの軸すべてにわたって並外れて整合しています。何も保証しませんが、この関係はほとんどの関係よりも多くを保てるという意味です。"},
    "FAVORABLE": {"headline": "成長できる組み合わせです。",
                  "body": "楽ではありませんが、構造的に支えられています。感じる摩擦は建設的な摩擦であり、破壊的なものではありません。"},
    "NEUTRAL": {"headline": "与えられるのではなく、築く関係です。",
                "body": "チャートは空白のキャンバスを与えています。二人がそれをどう描くかは完全にあなた方次第です。"},
    "CAUTION": {"headline": "多くを求める組み合わせです。",
                "body": "ここには本当の摩擦があります。離れる理由ではなく、早く、頻繁に、正直である理由です。"},
    "CHALLENGING": {"headline": "すべてを求める組み合わせです。",
                    "body": "構造があなた方に逆らって働いています。それが結果を決めるわけではありませんが、ほとんどの日に両方が意識して意志を持つ必要があるということです。"},
}

DISCLAIMER = (
    "ご案内：本相性レポートは、天文計算と現代の関係フレームワークを組み合わせたものです。"
    "象徴的で学派によって異なる読みであり、判決でも予測でもありません。"
    "正直な対話の代わりにはなりません。この関係の著者は、依然として二人です。"
)

RELATIONSHIP = {
    "romance": {"tip": "二人の情緒的な交流に注目してください。お互いの愛情表現の言語を理解すれば、不要な誤解を防げます。"},
    "business": {"tip": "仕事のスタイルと意思決定の違いを認めてください。互いの強みを活かす役割分担が成功の鍵です。"},
    "friend": {"tip": "共有する経験と相互の尊重に焦点を当ててください。与えることと受け取ることのバランスを等しく保ちましょう。"},
    "family": {"tip": "世代間の違いを認め、健全な境界線を引きましょう。議論に勝つことより共感を優先してください。"},
}


def _is_ja(s: str) -> bool:
    return bool(s) and bool(KANA_RE.search(s))


def verify() -> bool:
    print("\n[verify]")
    data = json.loads(JA_COMPAT.read_text(encoding="utf-8"))
    ok = True
    for rel in ("romance", "business"):
        for grade in ("COMPLEMENTARY", "BALANCED", "MODERATE", "TENSION", "DEFAULT"):
            e = data["ELEMENT_CONTENT"][rel][grade]
            if not (_is_ja(e.get("headline", "")) and _is_ja(e.get("body", ""))):
                print(f"  [ERR] ELEMENT_CONTENT.{rel}.{grade}")
                ok = False
    for grade in ("PEAK", "FAVORABLE", "NEUTRAL", "CAUTION", "CHALLENGING"):
        e = data["OVERALL_CONTENT"][grade]
        if not (_is_ja(e.get("headline", "")) and _is_ja(e.get("body", ""))):
            print(f"  [ERR] OVERALL_CONTENT.{grade}")
            ok = False
    if not _is_ja(data.get("DISCLAIMER", "")):
        print("  [ERR] DISCLAIMER"); ok = False
    for rel in ("romance", "business", "friend", "family"):
        if not _is_ja(data.get("RELATIONSHIP_CONTENT", {}).get(rel, {}).get("tip", "")):
            print(f"  [ERR] RELATIONSHIP_CONTENT.{rel}"); ok = False
    if ok:
        print("  [OK] ELEMENT_CONTENT romance/business = JA")
        print("  [OK] OVERALL_CONTENT = JA")
        print("  [OK] DISCLAIMER = JA")
        print("  [OK] RELATIONSHIP_CONTENT = JA")
    return ok


def main() -> int:
    print("=" * 60)
    print("[Phase 4-1] JA compatibility — ELEMENT_CONTENT(romance/business) + OVERALL + DISCLAIMER + RELATIONSHIP")
    print("=" * 60)
    if not JA_COMPAT.exists():
        print(f"❌ 파일 없음: {JA_COMPAT}"); return 1

    data = json.loads(JA_COMPAT.read_text(encoding="utf-8"))
    for rel in ("romance", "business"):
        data.setdefault("ELEMENT_CONTENT", {}).setdefault(rel, {}).update(ELEMENT[rel])
    data.setdefault("OVERALL_CONTENT", {}).update(OVERALL)
    data["DISCLAIMER"] = DISCLAIMER
    data["RELATIONSHIP_CONTENT"] = RELATIONSHIP

    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(payload)
    JA_COMPAT.write_text(payload, encoding="utf-8")
    print("✅ 저장 완료")

    ok = verify()
    print("=" * 60)
    if not ok:
        print("❌ verify 실패"); return 1
    print("🎉 Phase 4-1 완료")
    return 0


if __name__ == "__main__":
    sys.exit(main())