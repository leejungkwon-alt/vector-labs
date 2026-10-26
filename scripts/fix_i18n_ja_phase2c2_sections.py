#!/usr/bin/env python3
"""
Phase 2-C2 (JA): sections.json WORK_CONTENT 배치 2/3 (7 modes).
- THE_CREATOR, THE_CHALLENGER, THE_OFFICER, THE_SURVIVOR,
  THE_MYSTIC, THE_MENTOR, THE_GENERALIST
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JA_SECTIONS = ROOT / "app" / "services" / "content" / "data" / "ja" / "sections.json"


TRANSLATIONS = {
    "THE_CREATOR": {
        "headline": "自分の痕跡を仕事に見いだせるときに、あなたは輝きます。",
        "body": (
            "意味のない雑務が我慢なりません。ゼロから何かを築くか、"
            "自分だけの声を加える必要があります。\n\n"
            "頭の中はいつもアイデアで渦巻いています。"
            "それを世に送り出し、誰かを刺激したときに最大の達成感を味わいます。"
            "自律性が保証された環境でこそ、創造力を存分に発揮できます。\n\n"
            "ただ、創造者であることの痛みも受け入れる必要があります。"
            "アイデアが尽きたときや、仕事が過小評価されたときに、"
            "あなたは傷つきやすい。"
            "結果から距離を置き、プロセスそのものを楽しむ術を身につけましょう。"
        ),
        "patterns": [
            "ルールよりも自律性を重んじます。",
            "アイデアを現実にする実行力を備えています。",
            "批判に敏感に反応します。",
        ],
        "best_match": ["THE_OFFICER", "THE_MENTOR"],
        "best_reason": "あなたの創造性を体系化し、後押ししてくれる人です。",
        "challenging_match": ["THE_OFFICER"],
        "challenging_reason": "規則だけを押しつける上司とは正面衝突します。",
        "actions": [
            "創作のための没頭時間を週5時間確保しましょう。",
            "成果物を80%の状態で世に出してみましょう。",
            "批判を個人への攻撃ではなく、フィードバックとして受け止めましょう。",
        ],
        "red_flags": [
            "完璧主義のため締め切りに間に合っていませんか？",
            "上司の指示を無条件に無視していませんか？",
        ],
    },
    "THE_CHALLENGER": {
        "headline": "物事が壊れていて、直す必要があるときに、あなたは最高の力を発揮します。",
        "body": (
            "完璧な仕組みは要りません。必要なのは本物の問題です。"
            "何が機能していないかを、誰よりも早く見抜きます。\n\n"
            "あなたは現状維持を嫌う革新者です。"
            "「なぜこうやるのか？」と問い、より良い道を見つけます。"
            "危機のときにこそ真のリーダーシップを発揮します。\n\n"
            "ただ、批判が習慣になると、周囲はあなたをネガティブに見るかもしれません。"
            "問題を指摘するだけでなく、解決策と代替案を示しましょう。"
        ),
        "patterns": [
            "非効率を見逃すことができません。",
            "危機のときにリーダーシップを発揮します。",
            "権威に挑むことを恐れません。",
        ],
        "best_match": ["THE_CREATOR", "THE_OFFICER"],
        "best_reason": "あなたのアイデアを製品や仕組みに具現化してくれる人です。",
        "challenging_match": ["THE_OFFICER"],
        "challenging_reason": "既存のルールを重んじる人と衝突します。",
        "actions": [
            "不満を口にするときは、必ず「代替案」を添えましょう。",
            "上司の顔を立てる会話術を身につけましょう。",
            "同僚の意見を最後まで聞く練習をしましょう。",
        ],
        "red_flags": [
            "反対のための反対をしていませんか？",
            "あなたのせいでチームが縮こまっていませんか？",
        ],
    },
    "THE_OFFICER": {
        "headline": "体系化された組織で、信頼される中核人材です。",
        "body": (
            "原則とプロセスを重んじます。"
            "ルールが明確で、仕組みがしっかり整った組織で最も安定的に成果を出します。\n\n"
            "公正さと責任感が強く、上司と同僚から厚い信頼を得ます。"
            "大企業・公共機関・金融・法律など、体系が重要な分野に適しています。\n\n"
            "ただ、変化の速い環境や基準の曖昧な組織では、窮屈に感じるかもしれません。"
            "ときにルールより柔軟な対応が必要だということを覚えておきましょう。"
        ),
        "patterns": [
            "任されたことは必ず最後までやり遂げます。",
            "ヒエラルキーと報告の流れを重んじます。",
            "リスクを事前に防ぐ能力に優れています。",
        ],
        "best_match": ["THE_CHALLENGER", "THE_PIONEER"],
        "best_reason": "あなたの仕組みの上に新しい変化を乗せてくれる革新者です。",
        "challenging_match": ["THE_CHALLENGER"],
        "challenging_reason": "ルールを破りたがる人とは摩擦が生まれます。",
        "actions": [
            "新しい業務ツールを学び、仕事を自動化しましょう。",
            "上司の指示が不当なときは、データで説得しましょう。",
            "若い同僚のアイデアを受け入れる練習をしましょう。",
        ],
        "red_flags": [
            "「昔からこうやってきた」を口癖にしていませんか？",
            "変化を拒んで立ち遅れていませんか？",
        ],
    },
    "THE_SURVIVOR": {
        "headline": "他者が折れてしまうようなプレッシャーの中で、あなたは鍛え上げられます。",
        "body": (
            "多くの人より高いストレス限界を持っています。"
            "危機のときにこそ集中力が高まり、"
            "他の人が不可能だと言うときにも、やり遂げる粘りを発揮します。\n\n"
            "営業・構造改革・危機管理など、強いプレッシャーが伴う分野で頭角を現します。"
            "一度目標を決めたら、なりふり構わず突き進みます。\n\n"
            "ただ、過度な強さは周囲に「冷たい」「非情」という誤解を与えます。"
            "ときに弱さを見せることも、リーダーシップの一形態です。"
        ),
        "patterns": [
            "危機の最中でも平静を保ちます。",
            "目標への執念が強いです。",
            "感情表現が苦手です。",
        ],
        "best_match": ["THE_MENTOR", "THE_FLOW"],
        "best_reason": "あなたの鋭さを優しく包み込んでくれる人です。",
        "challenging_match": ["THE_SURVIVOR"],
        "challenging_reason": "二人とも攻撃的だと、チームが被害を受けます。",
        "actions": [
            "週に一日は完全に休む日と決めましょう。",
            "同僚に先に感謝を伝えましょう。",
            "運動や趣味でストレスを解消しましょう。",
        ],
        "red_flags": [
            "バーンアウトのサインを無視して走っていませんか？",
            "同僚があなたを恐れていませんか？",
        ],
    },
    "THE_MYSTIC": {
        "headline": "他の人が見落とす本質と構造を見抜きます。",
        "body": (
            "表面の現象ではなく、その奥の原理を掘り下げます。"
            "複雑なデータや状況を分析し、核心を抽出するのに卓越しています。\n\n"
            "研究・戦略企画・データ分析・コンサルティングなど、"
            "深い思考を要する分野で並外れた成果を出します。"
            "直感と洞察力に優れ、他の人が見落とすつながりを見つけ出します。\n\n"
            "ただ、考えすぎると実行が遅れます。"
            "完璧な絵が描ける前に、まず始める勇気を持ちましょう。"
        ),
        "patterns": [
            "行動の前に多くの分析をします。",
            "直感的な洞察力に優れています。",
            "表面的な仕事に退屈します。",
        ],
        "best_match": ["THE_PIONEER", "THE_CHALLENGER"],
        "best_reason": "あなたの分析を実際の行動に移してくれる実行者です。",
        "challenging_match": ["THE_GENERALIST"],
        "challenging_reason": "深みのない人とは話が通じません。",
        "actions": [
            "分析後3日以内に、必ず最初の一歩を踏み出しましょう。",
            "あなたの分析を可視化して、同僚と共有しましょう。",
            "実行力の強いパートナーを探しましょう。",
        ],
        "red_flags": [
            "分析ばかりして、機会を逃していませんか？",
            "自分だけの世界に没入しすぎていませんか？",
        ],
    },
    "THE_MENTOR": {
        "headline": "人の潜在能力を引き出すことに卓越しています。",
        "body": (
            "他の人の強みを見出し、育てることに生まれつきの才能があります。"
            "教え、助言することを楽しみ、"
            "後輩の成長に大きなやりがいを感じます。\n\n"
            "教育・HR・コンサルティング・マネジメント分野で優れた力を発揮します。"
            "あなたが通ったチームは、あなたが去った後もその文化を引き継ぎます。\n\n"
            "ただ、他人の成長に没頭するあまり、"
            "自分の成長を見失うことがあります。"
            "あなたも学び、成長していることを示すとき、より大きな尊敬を得ます。"
        ),
        "patterns": [
            "後輩の悩みをよく聞きます。",
            "知識を共有することを好みます。",
            "自分の成果を後回しにする傾向があります。",
        ],
        "best_match": ["THE_SURVIVOR", "THE_CREATOR"],
        "best_reason": "あなたの温かい助言を受け止め、成果で応えてくれる人です。",
        "challenging_match": ["THE_SURVIVOR"],
        "challenging_reason": "一匹狼タイプとは息が合わないことがあります。",
        "actions": [
            "自分のキャリア目標を明確に定義しましょう。",
            "教える立場を超えて、自分自身の専門性を確立しましょう。",
            "メンティーから学ぶ姿勢も見せましょう。",
        ],
        "red_flags": [
            "後輩だけを世話して、自分の評価は低くありませんか？",
            "教えることだけに安住していませんか？",
        ],
    },
    "THE_GENERALIST": {
        "headline": "多様な分野を横断しながら、シナジーを生み出します。",
        "body": (
            "ひとつの井戸だけを掘る専門家ではありません。"
            "代わりに、複数の領域の知識をつなげ、"
            "新しい価値を創り出す「T字型人材」です。\n\n"
            "企画・PM・プロジェクトマネジメントなど、"
            "多様なステークホルダーの間で潤滑油の役割を果たす職務に適しています。"
            "変化に柔軟に適応し、どんな組織でも生き残ります。\n\n"
            "ただ、深みがないという評価を受けることがあります。"
            "広い視野が強みになるためには、"
            "少なくとも一つの分野で誰にも負けない「スパイク」を作る必要があります。"
        ),
        "patterns": [
            "好奇心旺盛で、学ぶことを楽しみます。",
            "状況に合わせて役割を柔軟に変えます。",
            "集中力が分散することがあります。",
        ],
        "best_match": ["THE_MYSTIC", "THE_BLADE"],
        "best_reason": "あなたの多様なアイデアを、一つの戦略へと統合してくれる人です。",
        "challenging_match": ["THE_OFFICER"],
        "challenging_reason": "一つのルールだけを押しつける人とは、息苦しさを感じます。",
        "actions": [
            "今年集中する一つの専門分野を選びましょう。",
            "多様なネットワークを活かして、協働の機会を作りましょう。",
            "あなたの経験をコンテンツとしてまとめてみましょう。",
        ],
        "red_flags": [
            "あれこれ手を出して、仕上げができていませんか？",
            "専門家と呼ばれるために努力していますか？",
        ],
    },
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict) -> None:
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(payload)
    path.write_text(payload, encoding="utf-8")


def deep_merge(base: dict, override: dict) -> dict:
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            deep_merge(base[k], v)
        else:
            base[k] = v
    return base


def main() -> int:
    print("=" * 60)
    print("[Phase 2-C2/3 — JA] sections.json WORK_CONTENT (배치 2, 7 modes)")
    print("=" * 60)

    if not JA_SECTIONS.exists():
        print(f"❌ {JA_SECTIONS} 없음")
        return 1

    data = load_json(JA_SECTIONS)
    work = data.get("WORK_CONTENT")
    if not isinstance(work, dict):
        print("❌ WORK_CONTENT 없음")
        return 1

    for key, ov in TRANSLATIONS.items():
        if key not in work:
            print(f"❌ {key}: 기존 파일에 없음")
            return 1
        # 모드 키 검증
        for mode_key in ov["best_match"]:
            if not mode_key.startswith("THE_"):
                print(f"❌ {key}.best_match: 잘못된 모드 키 {mode_key!r}")
                return 1
        deep_merge(work[key], ov)
        print(f"✅ {key}: best_match={ov['best_match']} 유지")

    save_json(JA_SECTIONS, data)
    print(f"\n✅ {JA_SECTIONS.name} 저장 완료")

    # ── 검증
    print("\n[verify]")
    data2 = load_json(JA_SECTIONS)
    work2 = data2["WORK_CONTENT"]

    checks = [
        "THE_CREATOR", "THE_CHALLENGER", "THE_OFFICER", "THE_SURVIVOR",
        "THE_MYSTIC", "THE_MENTOR", "THE_GENERALIST",
    ]
    ok = True
    for key in checks:
        head = work2[key]["headline"]
        has_jp = any("\u3040" <= ch <= "\u30ff" or "\u4e00" <= ch <= "\u9fff" for ch in head)
        if has_jp and len(head) > 5:
            print(f"  [OK] {key}.headline = {head[:40]}")
        else:
            print(f"  [ERR] {key}.headline = {head!r}")
            ok = False
        bm = work2[key]["best_match"]
        if all(m.startswith("THE_") for m in bm):
            print(f"  [OK] {key}.best_match 키 보존 = {bm}")
        else:
            print(f"  [ERR] {key}.best_match 오염됨 = {bm}")
            ok = False

    # 2-C1 회귀 방지
    money_head = data2.get("MONEY_CONTENT", {}).get("THE_STEWARD", {}).get("headline", "")
    if any("\u3040" <= ch <= "\u30ff" or "\u4e00" <= ch <= "\u9fff" for ch in money_head):
        print("  [OK] 배치1(MONEY_CONTENT) 유지")
    else:
        print(f"  [ERR] 배치1 손상 — MONEY.THE_STEWARD.headline = {money_head!r}")
        ok = False

    # 다음 배치 의도된 영어 잔여
    bonds_head = data2.get("BONDS_CONTENT", {}).get("THE_TWIN", {}).get("headline", "")
    if "equal" in bonds_head.lower() or "comrade" in bonds_head.lower():
        print("  [OK] BONDS_CONTENT 영어 유지 (2-C3 대상, 의도)")

    if ok:
        print("\n[Phase 2-C2 OK] 다음: python -m pytest -q")
        print('  git add -A; git commit -m "i18n(ja): sections work batch 2/3"')
    else:
        print("\n[Phase 2-C2 FAIL] 위 로그 확인")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())