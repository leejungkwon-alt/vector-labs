#!/usr/bin/env python3
"""
Phase 5-6: JA premium_insights.json (41 units, ja 완주)
- TIMING 아래 전부 번역:
  * ten_god_labels (10) / grade_labels (5)
  * daewoon_narratives (3) : {pillar},{start_age},{end_age},{section_angle}
  * section_daewoon_angle (3×3=9)
  * year_narrative (1) : {target_year},{ten_god_label},{domain_kr}
  * domain_labels (3)
  * month_opportunity_narrative (1) : {month},{pillar},{section_angle}
  * month_caution_narrative (1)     : {month},{pillar},{section_angle}
  * section_month_angle (3×2=6)
  * no_daewoon (1) / disclaimer (1)

Idempotency: en 원본과 다르면 이미 번역 → skip.
Placeholder 검증: 6개 템플릿 세트 (필드별 필수 세트 다름) 정확 보존 시 저장.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JA = ROOT / "app" / "services" / "content" / "data" / "ja" / "premium_insights.json"
EN = ROOT / "app" / "services" / "content" / "data" / "en" / "premium_insights.json"

PLACEHOLDER_RE = re.compile(r"\{([a-z_]+)\}")

# TIMING 안의 경로 → 필수 placeholder 집합
PLACEHOLDER_REQUIREMENTS = {
    "daewoon_narratives.favorable": {"pillar", "start_age", "end_age", "section_angle"},
    "daewoon_narratives.neutral":   {"pillar", "start_age", "end_age", "section_angle"},
    "daewoon_narratives.caution":   {"pillar", "start_age", "end_age", "section_angle"},
    "year_narrative":               {"target_year", "ten_god_label", "domain_kr"},
    "month_opportunity_narrative":  {"month", "pillar", "section_angle"},
    "month_caution_narrative":      {"month", "pillar", "section_angle"},
}

TRANSLATIONS = {
    "ten_god_labels": {
        "TEN_GOD_FRIEND":          "仲間のエネルギー",
        "TEN_GOD_ROB_WEALTH":      "競争のエネルギー",
        "TEN_GOD_EATING_GOD":      "楽しみのエネルギー",
        "TEN_GOD_HURTING_OFFICER": "表現のエネルギー",
        "TEN_GOD_INDIRECT_WEALTH": "機会を掴むエネルギー",
        "TEN_GOD_DIRECT_WEALTH":   "管理するエネルギー",
        "TEN_GOD_SEVEN_KILLINGS":  "突破のエネルギー",
        "TEN_GOD_DIRECT_OFFICER":  "秩序のエネルギー",
        "TEN_GOD_INDIRECT_RESOURCE": "直感のエネルギー",
        "TEN_GOD_DIRECT_RESOURCE":   "学びのエネルギー",
    },
    "grade_labels": {
        "PEAK":        "最高潮",
        "FAVORABLE":   "順調",
        "NEUTRAL":     "均衡",
        "CAUTION":     "注意",
        "CHALLENGING": "難しさ",
    },
    "daewoon_narratives": {
        "favorable": (
            "今あなたは{start_age}歳から{end_age}歳まで続く{pillar}の"
            "人生の大きな流れの中にいます。"
            "この時期はあなたのリズムを後押しする強い追い風があります。"
            "{section_angle}"
        ),
        "neutral": (
            "今あなたは{start_age}歳から{end_age}歳まで続く{pillar}の"
            "人生の大きな流れの中にいます。"
            "この時期は追い風と向かい風が混ざっているので、"
            "同じ状況でも選択によって体感が大きく変わります。{section_angle}"
        ),
        "caution": (
            "今あなたは{start_age}歳から{end_age}歳まで続く{pillar}の"
            "人生の大きな流れの中にいます。"
            "この時期は自分自身をより丁寧にケアする必要があります。{section_angle}"
        ),
    },
    "section_daewoon_angle": {
        "love": {
            "favorable": (
                "関係では、心が自然に開いて、相手とのリズムが合いやすい時です。"
                "流れが良いほど、相手のペースを先に尋ねてみましょう。"
                "その余裕が関係をより深くします。"
            ),
            "neutral": (
                "関係では、近づくことと一歩引くことのバランスが大切です。"
                "互いの違いが表に出るとき、"
                "その場面で自分が何を確かめたいのか、自問してみてください。"
            ),
            "caution": (
                "関係では、同じシグナルも違う意味に解釈されやすい時です。"
                "大切な会話の前に一度深呼吸して、"
                "確信よりも「確認」を選びましょう。"
            ),
        },
        "career": {
            "favorable": (
                "仕事では、判断が比較的クリアに働きます。"
                "後回しにしていた提案や責任を手放すのに良い流れです。"
            ),
            "neutral": (
                "仕事では、拡張と整備のバランスを問われる流れです。"
                "新しい試みと既存のルーティンのどちらに時間を多く使うか、"
                "自分で決めてみてください。"
            ),
            "caution": (
                "仕事では、エネルギーが分散しやすく、"
                "決断を急ぐと疲労が大きくなります。"
                "この時期は「やらないこと」を先に決めるのが効果的です。"
            ),
        },
        "wealth": {
            "favorable": (
                "お金については、すでに持っているものを育てる方向がよく合います。"
                "大きな冒険よりも、管理の正確さが結果を作ります。"
            ),
            "neutral": (
                "お金については、収入と支出のリズムが一緒に揺れやすい時期です。"
                "大きな出費の前に一度確認する習慣が違いを生みます。"
            ),
            "caution": (
                "お金については、判断がぼやける瞬間が来るかもしれません。"
                "衝動的な決定を避け、支払いの前に一日の余裕を置きましょう。"
            ),
        },
    },
    "year_narrative": (
        "今年（{target_year}年）の大きなエネルギーは「{ten_god_label}」です。"
        "このエネルギーがあなたの{domain_kr}でどう現れるか、"
        "以下の流れと共に見てみてください。"
    ),
    "domain_labels": {
        "love":   "関係",
        "career": "仕事",
        "wealth": "富",
    },
    "month_opportunity_narrative": (
        "{month}月（{pillar}）は、今年の流れの中で、"
        "あなたにとって比較的自然に扉が開く月です。{section_angle}"
    ),
    "month_caution_narrative": (
        "{month}月（{pillar}）は、今年の流れの中で、"
        "特に判断に注意が必要な月です。{section_angle}"
    ),
    "section_month_angle": {
        "love": {
            "opportunity": (
                "関係で心が通じ合う場面が増えるかもしれません。"
                "流れが良いほど、相手の話を最後まで聞く練習が深さを生みます。"
            ),
            "caution": (
                "関係で誤解が積み重なりやすい月です。"
                "決断の前に、相手の意図をもう一度確認してください。"
            ),
        },
        "career": {
            "opportunity": (
                "仕事で提案・協働・面接など、扉を叩く試みがよく合う月です。"
            ),
            "caution": (
                "仕事で感情的な消耗が大きくなりやすい月です。"
                "大切な決断は体調の良い日に先延ばししましょう。"
            ),
        },
        "wealth": {
            "opportunity": (
                "お金については、管理・整理・契約に有利な月です。"
                "すでに計画していたことを実行に移すのが良いでしょう。"
            ),
            "caution": (
                "お金については、衝動的な判断に揺れやすい月です。"
                "大きな支出は一日後ろに延ばしてください。"
            ),
        },
    },
    "no_daewoon": (
        "人生の大きな流れの詳細はまだ十分に現れていないため、"
        "今年の流れと今月のエネルギーを中心に読みます。"
    ),
    "disclaimer": (
        "ご案内：この時期の解釈は決定論的な予測ではなく、"
        "今の流れを読むためのコーチングの視点です。"
        "人生の選択は、いつでもあなたのものです。"
    ),
}


def _walk(ja_node, en_node, trans_node, path=""):
    """en 원본과 동일하면 번역으로 교체, 다르면 skip."""
    applied = skipped = 0
    for key, tv in trans_node.items():
        en_sub = en_node.get(key) if isinstance(en_node, dict) else None
        cur_path = f"{path}.{key}" if path else key

        if isinstance(tv, dict):
            ja_sub = ja_node.setdefault(key, {})
            a, s = _walk(ja_sub, en_sub or {}, tv, cur_path)
            applied += a
            skipped += s
        else:
            if ja_node.get(key) == en_sub:
                ja_node[key] = tv
                print(f"✅ {cur_path}")
                applied += 1
            else:
                print(f"⏭️  {cur_path}: 이미 번역됨")
                skipped += 1
    return applied, skipped


def _check_placeholders(timing: dict) -> list:
    """필수 placeholder 집합이 정확히 보존됐는지 검증."""
    errors = []
    for dotted, required in PLACEHOLDER_REQUIREMENTS.items():
        node = timing
        for part in dotted.split("."):
            if not isinstance(node, dict) or part not in node:
                errors.append(f"{dotted}: 필드 없음")
                node = None
                break
            node = node[part]
        if node is None:
            continue
        if not isinstance(node, str):
            errors.append(f"{dotted}: 문자열 아님")
            continue
        found = set(PLACEHOLDER_RE.findall(node))
        if found != required:
            errors.append(
                f"{dotted}: placeholder 불일치 — 필요={sorted(required)}, 발견={sorted(found)}"
            )
    return errors


def main() -> int:
    ja_data = json.loads(JA.read_text(encoding="utf-8"))
    en_data = json.loads(EN.read_text(encoding="utf-8"))

    if "TIMING" not in ja_data or "TIMING" not in en_data:
        print("❌ TIMING 키 없음 — 파일 구조 확인 필요")
        return 1

    ja_timing = ja_data["TIMING"]
    en_timing = en_data["TIMING"]

    applied, skipped = _walk(ja_timing, en_timing, TRANSLATIONS)
    print(f"\n결과: applied={applied}, skipped={skipped}")

    # ---- 저장 전 placeholder 사전검증 ----
    print("\n[placeholders]")
    ph_errors = _check_placeholders(ja_timing)
    if ph_errors:
        for e in ph_errors:
            print(f"  ❌ {e}")
        print("저장 취소 — placeholder 손상 위험")
        return 1
    print("  ✅ 6개 템플릿 필드의 placeholder 모두 보존")

    # 저장 전 사전검증
    payload = json.dumps(ja_data, ensure_ascii=False, indent=2) + "\n"
    json.loads(payload)
    JA.write_text(payload, encoding="utf-8")

    # ---- 최종 검증 ----
    print("\n[verify]")
    data = json.loads(JA.read_text(encoding="utf-8"))["TIMING"]
    en = en_data["TIMING"]
    all_ok = True

    def _eq_check(label, ja_val, en_val):
        nonlocal all_ok
        ok = ja_val != en_val
        print(f"  {'✅' if ok else '❌'} {label} = JA")
        if not ok:
            all_ok = False

    # ten_god_labels
    tg_ok = all(data["ten_god_labels"].get(k) != en["ten_god_labels"].get(k)
                for k in TRANSLATIONS["ten_god_labels"])
    print(f"  {'✅' if tg_ok else '❌'} ten_god_labels (10) = JA")
    all_ok &= tg_ok

    # grade_labels
    gl_ok = all(data["grade_labels"].get(k) != en["grade_labels"].get(k)
                for k in TRANSLATIONS["grade_labels"])
    print(f"  {'✅' if gl_ok else '❌'} grade_labels (5) = JA")
    all_ok &= gl_ok

    # daewoon_narratives
    dn_ok = all(data["daewoon_narratives"].get(k) != en["daewoon_narratives"].get(k)
                for k in ("favorable", "neutral", "caution"))
    print(f"  {'✅' if dn_ok else '❌'} daewoon_narratives (3) = JA (placeholders 보존)")
    all_ok &= dn_ok

    # section_daewoon_angle
    sda_ok = all(
        data["section_daewoon_angle"][d][k] != en["section_daewoon_angle"][d][k]
        for d in ("love", "career", "wealth")
        for k in ("favorable", "neutral", "caution")
    )
    print(f"  {'✅' if sda_ok else '❌'} section_daewoon_angle (3×3) = JA")
    all_ok &= sda_ok

    # year_narrative
    _eq_check("year_narrative (placeholders 보존)",
              data["year_narrative"], en["year_narrative"])

    # domain_labels
    dl_ok = all(data["domain_labels"].get(k) != en["domain_labels"].get(k)
                for k in ("love", "career", "wealth"))
    print(f"  {'✅' if dl_ok else '❌'} domain_labels (3) = JA")
    all_ok &= dl_ok

    # month_opportunity_narrative / month_caution_narrative
    _eq_check("month_opportunity_narrative (placeholders 보존)",
              data["month_opportunity_narrative"], en["month_opportunity_narrative"])
    _eq_check("month_caution_narrative (placeholders 보존)",
              data["month_caution_narrative"], en["month_caution_narrative"])

    # section_month_angle
    sma_ok = all(
        data["section_month_angle"][d][k] != en["section_month_angle"][d][k]
        for d in ("love", "career", "wealth")
        for k in ("opportunity", "caution")
    )
    print(f"  {'✅' if sma_ok else '❌'} section_month_angle (3×2) = JA")
    all_ok &= sma_ok

    # no_daewoon / disclaimer
    _eq_check("no_daewoon", data["no_daewoon"], en["no_daewoon"])
    _eq_check("disclaimer", data["disclaimer"], en["disclaimer"])

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())