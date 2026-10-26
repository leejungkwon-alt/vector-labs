#!/usr/bin/env python3
"""
Phase 2-C3 (JA): sections.json BONDS_CONTENT 배치 3/3 (마지막).
- THE_TWIN, THE_RIVAL, THE_ALLY, THE_EMPATH

이 스크립트 완료로 sections.json 전체가 일본어화됨.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JA_SECTIONS = ROOT / "app" / "services" / "content" / "data" / "ja" / "sections.json"


TRANSLATIONS = {
    "THE_TWIN": {
        "headline": "対等な関係の中で最もくつろげます。",
        "body": (
            "誰かを導いたり、誰かに頼ったりするのが好きではありません。"
            "同じ高さで目を合わせ、共に同じ方向へ歩むパートナーを望みます。\n\n"
            "互いの違いを認め、共に成長する関係を最も理想的と考えます。"
            "互いに負担をかけず、それでいて深い絆を形づくります。\n\n"
            "ただ、「クール」な関係だけを追い求めすぎると、"
            "深い親密さを築くのが難しくなります。"
            "ときに互いに寄りかかり、頼ることも覚えましょう。"
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
            "一緒に楽しめる趣味を一つ作りましょう。",
        ],
        "red_flags": [
            "無関心すぎて、相手が寂しさを感じていませんか？",
            "喧嘩を避けるために感情を隠していませんか？",
        ],
    },
    "THE_RIVAL": {
        "headline": "互いに刺激し合う健全な競争を楽しみます。",
        "body": (
            "無条件に同意してくれる人よりも、"
            "進んで議論し、押し返してくれる人を求めます。\n\n"
            "異なる意見を交わし、ときに鋭くフィードバックし合いながら、"
            "互いを鍛えていきます。"
            "そうした関係は退屈する暇がなく、"
            "常に相手から学び続けることができます。\n\n"
            "ただ、すべての会話を議論にする必要はありません。"
            "相手が今、慰めを求めているのか、"
            "助言を求めているのかを見抜く共感力が必要です。"
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
            "誰とでも気軽に付き合うタイプではありません。"
            "慎重に選び、一度自分の人と決めたら長く続きます。"
            "あなたの忠誠心は静かですが、とても強いものです。\n\n"
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
            "人の気分を素早く正確に読み取ります。"
            "本人より先に、気分が良くないことに気づきます。"
            "だからこそ、稀な良い友人になります。\n\n"
            "言葉にしなくても心を理解してくれるあなたの傍らに、"
            "人々が集まってきます。"
            "あなたは相手に深い情緒的な安定感を与えます。\n\n"
            "ただ、他人の感情に入り込みすぎると、"
            "自分の感情をいたわらずに疲弊してしまいます。"
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
    print("[Phase 2-C3/3 — JA] sections.json BONDS_CONTENT (배치 3, 마지막)")
    print("=" * 60)

    if not JA_SECTIONS.exists():
        print(f"❌ {JA_SECTIONS} 없음")
        return 1

    data = load_json(JA_SECTIONS)
    bonds = data.get("BONDS_CONTENT")
    if not isinstance(bonds, dict):
        print("❌ BONDS_CONTENT 없음")
        return 1

    for key, ov in TRANSLATIONS.items():
        if key not in bonds:
            print(f"❌ {key}: 기존 파일에 없음")
            return 1
        for mode_key in ov["best_match"]:
            if not mode_key.startswith("THE_"):
                print(f"❌ {key}.best_match: 잘못된 모드 키 {mode_key!r}")
                return 1
        deep_merge(bonds[key], ov)
        print(f"✅ {key}: best_match={ov['best_match']} 유지")

    save_json(JA_SECTIONS, data)
    print(f"\n✅ {JA_SECTIONS.name} 저장 완료")

    # ── 검증
    print("\n[verify]")
    data2 = load_json(JA_SECTIONS)
    bonds2 = data2["BONDS_CONTENT"]

    checks = ["THE_TWIN", "THE_RIVAL", "THE_ALLY", "THE_EMPATH"]
    ok = True
    for key in checks:
        head = bonds2[key]["headline"]
        has_jp = any("\u3040" <= ch <= "\u30ff" or "\u4e00" <= ch <= "\u9fff" for ch in head)
        if has_jp and len(head) > 5:
            print(f"  [OK] {key}.headline = {head[:40]}")
        else:
            print(f"  [ERR] {key}.headline = {head!r}")
            ok = False
        bm = bonds2[key]["best_match"]
        if all(m.startswith("THE_") for m in bm):
            print(f"  [OK] {key}.best_match 키 보존 = {bm}")
        else:
            print(f"  [ERR] {key}.best_match 오염됨 = {bm}")
            ok = False

    # 배치 1/2 회귀 방지
    money_head = data2.get("MONEY_CONTENT", {}).get("THE_STEWARD", {}).get("headline", "")
    if any("\u3040" <= ch <= "\u30ff" or "\u4e00" <= ch <= "\u9fff" for ch in money_head):
        print("  [OK] 배치1(MONEY_CONTENT) 유지")
    else:
        print(f"  [ERR] 배치1 손상 — MONEY.THE_STEWARD.headline = {money_head!r}")
        ok = False

    work_head = data2.get("WORK_CONTENT", {}).get("THE_CREATOR", {}).get("headline", "")
    if any("\u3040" <= ch <= "\u30ff" or "\u4e00" <= ch <= "\u9fff" for ch in work_head):
        print("  [OK] 배치2(WORK_CONTENT) 유지")
    else:
        print(f"  [ERR] 배치2 손상 — WORK.THE_CREATOR.headline = {work_head!r}")
        ok = False

    # Phase 1 회귀 방지 (SECTION_TITLES / DISCLAIMER)
    section_titles = data2.get("SECTION_TITLES", {})
    if section_titles.get("core") == "あなたの本質":
        print("  [OK] Phase1(SECTION_TITLES) 유지")
    else:
        print(f"  [ERR] Phase1 손상 — SECTION_TITLES.core = {section_titles.get('core')!r}")
        ok = False
    disclaimer = data2.get("DISCLAIMER", "")
    if "四柱推命" in disclaimer:
        print("  [OK] Phase1(DISCLAIMER) 유지")
    else:
        print("  [ERR] Phase1 손상 — DISCLAIMER")
        ok = False

    # sections.json 전체 커버리지 점검: 6개 블록 헤드라인이 모두 일본어여야 함
    all_blocks = (
        [("MONEY_CONTENT", k) for k in ("THE_STEWARD", "THE_OPERATOR", "THE_FLOW")]
        + [("WORK_CONTENT", k) for k in (
            "THE_CREATOR", "THE_CHALLENGER", "THE_OFFICER", "THE_SURVIVOR",
            "THE_MYSTIC", "THE_MENTOR", "THE_GENERALIST",
        )]
        + [("BONDS_CONTENT", k) for k in ("THE_TWIN", "THE_RIVAL", "THE_ALLY", "THE_EMPATH")]
    )
    en_residue = []
    for section_key, block_key in all_blocks:
        head = data2.get(section_key, {}).get(block_key, {}).get("headline", "")
        has_jp = any("\u3040" <= ch <= "\u30ff" or "\u4e00" <= ch <= "\u9fff" for ch in head)
        if not has_jp:
            en_residue.append(f"{section_key}.{block_key}")
    if not en_residue:
        print(f"  [OK] sections.json 콘텐츠 블록 14개 전부 일본어화 완료")
    else:
        print(f"  [ERR] 영어 잔여: {en_residue}")
        ok = False

    if ok:
        print("\n[Phase 2-C 완료 — sections.json 전체 번역 완료]")
        print("  python -m pytest -q")
        print('  git add -A; git commit -m "i18n(ja): sections complete (money/work/bonds)"')
    else:
        print("\n[Phase 2-C3 FAIL] 위 로그 확인")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())