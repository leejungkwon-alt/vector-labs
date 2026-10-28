#!/usr/bin/env python3
"""
Phase 2-C1 (JA): sections.json MONEY_CONTENT 배치 1/3.
- THE_STEWARD, THE_OPERATOR, THE_FLOW

best_match/challenging_match 의 모드 키(THE_*)는 영어 그대로 유지.
프론트엔드 formatMode 가 로케일별 라벨로 변환함.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JA_SECTIONS = ROOT / "app" / "services" / "content" / "data" / "ja" / "sections.json"


TRANSLATIONS = {
    "THE_STEWARD": {
        "headline": "資産を安全に守り、複利で育てていきます。",
        "body": (
            "リスクを極端に嫌い、元本割れに耐えられません。"
            "目の前の短期リターンよりも、長期的な安定性を最優先に考えます。\n\n"
            "そうした気質は、預貯金・債券・不動産といった確実な安全資産を"
            "好む方向へと導きます。他の人が仮想通貨やデイトレードに"
            "熱狂しているとき、あなたは静かに資産を守り、育てます。\n\n"
            "ただ、過度な保守性はインフレに勝てないという結果を招きます。"
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
            "お金が流れることを楽しみます。資本を寝かせるよりも、"
            "新たな機会を捉えて回すことに長けています。\n\n"
            "副業・小規模事業・短期投資など、多方面で収益を生み出す感覚があります。"
            "速い決断力のおかげで、他の人がためらうとき大胆に賭け、"
            "大きなリターンを得ることもあります。\n\n"
            "ただ、すべての流れが速くなると、漏れる穴もまた大きくなります。"
            "キャッシュフローが良いときにセーフティネットを確保しなければ、"
            "危機に脆くなります。"
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
            "お金に対する固定観念がありません。"
            "人脈・直感・そして状況の流れに乗って、自然に収入を作り出します。\n\n"
            "あるときは大きなお金が入り、あるときは空っぽになります。"
            "それでもその流れを淡々と受け止め、必要な瞬間に機会を引き寄せる力があります。\n\n"
            "そうした柔軟さは強みですが、計画なく即興的に支出する癖は"
            "財政を危うくします。最低限のセーフティネットは不可欠です。"
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
            "口座を二つに分けましょう（緊急費 / 生活費）。",
            "大きな支出の前には必ず24時間待ちましょう。",
            "毎月の収入の10%は無条件で貯蓄しましょう。",
        ],
        "red_flags": [
            "カードの支払いを回し払いにしていませんか？",
            "知人の誘いで投資して損をしたことはありませんか？",
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
    print("[Phase 2-C1/3 — JA] sections.json MONEY_CONTENT (배치 1)")
    print("=" * 60)

    if not JA_SECTIONS.exists():
        print(f"❌ {JA_SECTIONS} 없음")
        return 1

    data = load_json(JA_SECTIONS)
    money = data.get("MONEY_CONTENT")
    if not isinstance(money, dict):
        print("❌ MONEY_CONTENT 없음")
        return 1

    for key, ov in TRANSLATIONS.items():
        if key not in money:
            print(f"❌ {key}: 기존 파일에 없음")
            return 1
        # 모드 키 보존 검증
        expected_best = set(ov["best_match"])
        for mode_key in expected_best:
            if not mode_key.startswith("THE_"):
                print(f"❌ {key}.best_match: 잘못된 모드 키 {mode_key!r}")
                return 1
        deep_merge(money[key], ov)
        print(f"✅ {key}: best_match={ov['best_match']} 유지")

    save_json(JA_SECTIONS, data)
    print(f"\n✅ {JA_SECTIONS.name} 저장 완료")

    # ── 검증
    print("\n[verify]")
    data2 = load_json(JA_SECTIONS)
    money2 = data2["MONEY_CONTENT"]

    checks = ["THE_STEWARD", "THE_OPERATOR", "THE_FLOW"]
    ok = True
    for key in checks:
        head = money2[key]["headline"]
        has_jp = any("\u3040" <= ch <= "\u30ff" or "\u4e00" <= ch <= "\u9fff" for ch in head)
        if has_jp and len(head) > 5:
            print(f"  [OK] {key}.headline = {head[:40]}")
        else:
            print(f"  [ERR] {key}.headline = {head!r}")
            ok = False
        # best_match 키 보존 확인
        bm = money2[key]["best_match"]
        if all(m.startswith("THE_") for m in bm):
            print(f"  [OK] {key}.best_match 키 보존 = {bm}")
        else:
            print(f"  [ERR] {key}.best_match 오염됨 = {bm}")
            ok = False

    # 다음 배치 의도된 영어 잔여
    work_head = data2.get("WORK_CONTENT", {}).get("THE_CREATOR", {}).get("headline", "")
    if "prosper" in work_head.lower() or "mark" in work_head.lower():
        print("  [OK] WORK_CONTENT 영어 유지 (2-C2 대상, 의도)")

    if ok:
        print("\n[Phase 2-C1 OK] 다음: python -m pytest -q")
        print('  git add -A; git commit -m "i18n(ja): sections money batch 1/3"')
    else:
        print("\n[Phase 2-C1 FAIL] 위 로그 확인")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())