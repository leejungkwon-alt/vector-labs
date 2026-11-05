#!/usr/bin/env python3
"""
Phase 5-5: JA cross_insight.json
- MODE_LABELS: 14 (display names)
- AXES: 8 × {pos, neg}
- ANGLES: 8 × {love, career, wealth} = 24
- BALANCED: intro + body + angle{3} = 5
- MODE_SECTION_LABEL: 3
- 템플릿 6종: INTRO_TEMPLATE, COLLISION_SENTENCE, COLLISION_2_SENTENCE,
              PULL_SENTENCE, PULL_2_SENTENCE, CLOSING_TEMPLATE(no placeholder)
- DISCLAIMER: 1
- MODE_AXES: 숫자 → 번역 안 함 (건드리지 않음)

Idempotency: en 원본과 다르면 이미 번역 → skip.
Placeholder 검증: 템플릿 필드 6개는 {xxx} 집합이 원본과 일치해야 저장.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JA = ROOT / "app" / "services" / "content" / "data" / "ja" / "cross_insight.json"
EN = ROOT / "app" / "services" / "content" / "data" / "en" / "cross_insight.json"

PLACEHOLDER_RE = re.compile(r"\{([a-z_]+)\}")

# 각 템플릿 필드에 반드시 있어야 하는 placeholder
REQUIRED_PLACEHOLDERS = {
    "INTRO_TEMPLATE":        {"bond_label", "work_label"},
    "BALANCED.intro":        {"bond_label", "work_label", "money_label"},
    "COLLISION_SENTENCE":    {"a_mode_label", "a_label", "b_mode_label", "b_label"},
    "COLLISION_2_SENTENCE":  {"a_mode_label", "a_label", "b_mode_label", "b_label"},
    "PULL_SENTENCE":         {"mode_label", "label"},
    "PULL_2_SENTENCE":       {"mode_label", "label"},
}

TRANSLATIONS = {
    "MODE_LABELS": {
        "THE_TWIN":         "相棒",
        "THE_RIVAL":        "ライバル",
        "THE_ALLY":         "味方",
        "THE_EMPATH":       "共感者",
        "THE_CREATOR":      "創造者",
        "THE_CHALLENGER":   "挑戦者",
        "THE_OFFICER":      "原理主義者",
        "THE_SURVIVOR":     "生存者",
        "THE_MYSTIC":       "探究者",
        "THE_MENTOR":       "メンター",
        "THE_GENERALIST":   "オールラウンダー",
        "THE_STEWARD":      "管理人",
        "THE_OPERATOR":     "運営者",
        "THE_FLOW":         "流れ",
    },
    "AXES": {
        "FREEDOM_BOND":               {"pos": "一緒にいること",         "neg": "一人の時間"},
        "RISK_SAFETY":                {"pos": "新しい挑戦",             "neg": "安定した基盤"},
        "DEPTH_BREADTH":              {"pos": "深く掘ること",           "neg": "広く経験すること"},
        "STRUCTURE_FLOW":             {"pos": "決まったルール",         "neg": "即興の流れ"},
        "EXPRESSION_RESTRAINT":       {"pos": "表現すること",           "neg": "節度ある態度"},
        "COMPETITION_COLLABORATION":  {"pos": "競争して勝つこと",       "neg": "協力して共に進むこと"},
        "SPEED_PATIENCE":             {"pos": "速く動くこと",           "neg": "ゆっくり熟成すること"},
        "SELF_OTHERS":                {"pos": "自分を優先すること",     "neg": "他人を優先すること"},
    },
    "INTRO_TEMPLATE": (
        "関係では互いに寄りかかる「{bond_label}」として、"
        "仕事では目標に向かって進む「{work_label}」として生きています。"
        "お金については執着するよりも、自然に流れに任せて受け入れるタイプです。"
    ),
    "ANGLES": {
        "FREEDOM_BOND": {
            "love": (
                "ですから、「近さはあるけれど、それぞれの部屋がある」関係がよく似合います。"
                "逆に、これが一気に求められる場面（たとえばビジネスパートナー同士の交際など）では、"
                "境界線を先に言葉にすることが長続きの秘訣です。"
            ),
            "career": (
                "ですから、「ひとりで完全に集中する時間」と「周りと呼吸を合わせる時間」の両方が必要です。"
                "どちらかが欠けると、疲れやすくなったり無気力になりやすい。"
            ),
            "wealth": (
                "ですから、お金についても「自分の決定」と「共有の決定」を混ぜるのが良いでしょう。"
                "大きなことはひとりで決め、実行は信頼できる人と分かち合う。"
            ),
        },
        "RISK_SAFETY": {
            "love": (
                "ですから、安定した人に惹かれますが、安定しすぎるともどかしくなります。"
                "関係の中に小さな新しさ（旅、新しい趣味など）を絶やさず作っていくと長続きします。"
            ),
            "career": (
                "ですから、挑戦と安定の間で揺れます。大きな決断の前に、"
                "「今、自分にセーフティネットはあるか？」を確認しましょう。"
                "セーフティネットがあれば、挑戦はずっと軽くなります。"
            ),
            "wealth": (
                "ですから、お金については「一度の大きな賭け」よりも「小さな実験を頻繁に」が向いています。"
                "失っても構わない範囲でだけ動きましょう。"
            ),
        },
        "DEPTH_BREADTH": {
            "love": (
                "ですから、「深く知るひとりの人」と「軽く出会うたくさんの人」の間で揺れます。"
                "どちらであれ、ときどき、自分のエネルギーをどこに注いでいるのかを確かめてください。"
            ),
            "career": (
                "ですから、ひとつの井戸を深く掘る時と、多くの分野を横断する時を区別する必要があります。"
                "今の自分にはどちらが合っているのか、自問してください。"
            ),
            "wealth": (
                "ですから、「集中投資」と「分散投資」のバランスが大切です。"
                "どちらにしても、片方に100%寄せるのは危険です。"
            ),
        },
        "STRUCTURE_FLOW": {
            "love": (
                "ですから、関係にルールを決めると心地よいですが、きつすぎると息苦しくなります。"
                "「守るべきことひとつ、自由にしておくことひとつ」を決めておきましょう。"
            ),
            "career": (
                "ですから、構造のある環境で強みを発揮しますが、柔軟さが消えると疲れます。"
                "ルーティンの中に、意識的に「即興性」を少し残しておきましょう。"
            ),
            "wealth": (
                "ですから、自動貯蓄のような「構造」があなたを救います。"
                "衝動的な支出が多いなら、まず構造を作るのが先決です。"
            ),
        },
        "EXPRESSION_RESTRAINT": {
            "love": (
                "ですから、気持ちを伝えたいのに、タイミングを逃すと誤解が積み重なります。"
                "一日に一度、「今、自分がどんな感情か」を声に出してみましょう。"
            ),
            "career": (
                "ですから、言いたいことがたくさんあります。ただ、表現が強すぎると関係を傷つけることも覚えておきましょう。"
                "「内容は明確に、トーンは柔らかく」。"
            ),
            "wealth": (
                "ですから、お金については「使いたい衝動」と「抑えたい衝動」がぶつかります。"
                "大きな出費の前に一日待つルールが効きます。"
            ),
        },
        "COMPETITION_COLLABORATION": {
            "love": (
                "ですから、互いに刺激し合う関係が好きですが、過剰になると消耗戦になります。"
                "「勝つ会話」と「一緒に解く会話」を区別しましょう。"
            ),
            "career": (
                "ですから、競争と協力のバランスが鍵です。"
                "誰と競い、誰と協力するのかを明確に決めると、エネルギーが節約できます。"
            ),
            "wealth": (
                "ですから、お金については「他人より先へ」よりも「自分のペースを守る」方が長続きします。"
                "比較は判断を曇らせます。"
            ),
        },
        "SPEED_PATIENCE": {
            "love": (
                "ですから、関係が早く深まることを望みますが、人にはそれぞれのペースがあります。"
                "相手のペースを尋ねることが信頼を築きます。"
            ),
            "career": (
                "ですから、早い結果を望みますが、"
                "「熟成させる仕事」と「今すぐ出す仕事」を区別しましょう。"
            ),
            "wealth": (
                "ですから、お金については「早いリターン」と「ゆっくり育てる」がぶつかります。"
                "二つを混ぜて回すのが一番安全です。"
            ),
        },
        "SELF_OTHERS": {
            "love": (
                "ですから、相手を気遣うあまり、自分の気持ちを見失います。"
                "「今、自分がどう感じているか」を先に伝えることが、関係を長持ちさせます。"
            ),
            "career": (
                "ですから、他人を助けるうちに、自分の評価を見失います。"
                "自分の成果を記録し、アピールする練習をしましょう。"
            ),
            "wealth": (
                "ですから、お金については「与える支出」と「自分のための貯蓄」を分けましょう。"
                "両方があってこそ長続きします。"
            ),
        },
    },
    "BALANCED": {
        "intro": (
            "関係では「{bond_label}」、仕事では「{work_label}」、"
            "お金は「{money_label}」のように扱います。"
        ),
        "body": (
            "この三つは大きな衝突なくバランスをとっています。"
            "強く突き出た軸がないということは、逆に言えば、自分で選べる余地が大きいということ。"
            "今、どの軸に重みを置くか、自分で決めてみてください。"
        ),
        "angle": {
            "love": (
                "関係では、ときどき相手のリズムを尋ねるだけで、バランスがより強固になります。"
            ),
            "career": (
                "仕事では、「自分がやりたいこと」と「今必要とされていること」を区別しましょう。"
            ),
            "wealth": (
                "お金については、貯蓄と支出の比率を一度整理しておくと、心が落ち着きます。"
            ),
        },
    },
    "CLOSING_TEMPLATE": (
        "これら三つが同時に求められるとき（たとえばビジネスパートナーとの交際、家業など）、"
        "「今、自分がどの軸に立っているか」を最初に言うことが、長続きの秘訣です。"
    ),
    "DISCLAIMER": (
        "ご案内：この組み合わせの解釈は決定論的な予測ではなく、"
        "三つの領域の傾向が出会う地点をコーチングの視点で読んだものです。"
        "人生の選択は、いつでもあなたのものです。"
    ),
    "MODE_SECTION_LABEL": {
        "bond":  "関係",
        "work":  "仕事",
        "money": "お金",
    },
    "COLLISION_SENTENCE": (
        "「{a_mode_label}」の「{a_label}」と「{b_mode_label}」の「{b_label}」の間で揺れています。"
    ),
    "COLLISION_2_SENTENCE": (
        "そこに、「{a_mode_label}」の「{a_label}」と「{b_mode_label}」の「{b_label}」の間の揺れも加わります。"
    ),
    "PULL_SENTENCE": (
        "さらに、「{mode_label}」の「{label}」の方へ心が傾いています。"
    ),
    "PULL_2_SENTENCE": (
        "そして、「{mode_label}」の「{label}」の方にも心が傾いています。"
    ),
}


def _walk(ja_node, en_node, trans_node, path=""):
    """재귀적으로 trans_node의 leaf를 순회하며 en 원본과 비교·교체."""
    applied = skipped = 0
    for key, tv in trans_node.items():
        ja_sub = ja_node.setdefault(key, {} if isinstance(tv, dict) else "")
        en_sub = en_node.get(key) if isinstance(en_node, dict) else None
        cur_path = f"{path}.{key}" if path else key

        if isinstance(tv, dict):
            applied += 0  # 재귀에서 집계
            a, s = _walk(ja_sub, en_sub or {}, tv, cur_path)
            applied += a
            skipped += s
        else:
            if ja_sub == en_sub:  # 여전히 영문 → 번역
                ja_node[key] = tv
                print(f"✅ {cur_path}")
                applied += 1
            else:
                print(f"⏭️  {cur_path}: 이미 번역됨")
                skipped += 1
    return applied, skipped


def _check_placeholders(data: dict) -> list:
    """필수 placeholder 집합이 정확히 보존됐는지 검증."""
    errors = []
    for dotted, required in REQUIRED_PLACEHOLDERS.items():
        node = data
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

    applied, skipped = _walk(ja_data, en_data, TRANSLATIONS)
    print(f"\n결과: applied={applied}, skipped={skipped}")

    # ---- 저장 전 사전검증 (placeholder 포함) ----
    print("\n[placeholders]")
    ph_errors = _check_placeholders(ja_data)
    if ph_errors:
        for e in ph_errors:
            print(f"  ❌ {e}")
        print("저장 취소 — placeholder 손상 위험")
        return 1
    print(f"  ✅ 6개 템플릿 placeholder 모두 보존")

    # ---- MODE_AXES 무손상 검증 ----
    if ja_data.get("MODE_AXES") != en_data.get("MODE_AXES"):
        print("  ❌ MODE_AXES 변형됨 (숫자 데이터여야 함)")
        return 1
    print("  ✅ MODE_AXES 원본과 동일 (숫자 유지)")

    payload = json.dumps(ja_data, ensure_ascii=False, indent=2) + "\n"
    json.loads(payload)
    JA.write_text(payload, encoding="utf-8")

    # ---- 최종 검증 ----
    print("\n[verify]")
    data = json.loads(JA.read_text(encoding="utf-8"))
    en_c = en_data
    all_ok = True

    # MODE_LABELS
    labels_ok = all(
        data["MODE_LABELS"].get(k) != en_c["MODE_LABELS"].get(k)
        for k in TRANSLATIONS["MODE_LABELS"]
    )
    print(f"  {'✅' if labels_ok else '❌'} MODE_LABELS ({len(TRANSLATIONS['MODE_LABELS'])}) = JA")
    all_ok &= labels_ok

    # AXES
    axes_ok = all(
        data["AXES"][k].get("pos") != en_c["AXES"][k].get("pos")
        and data["AXES"][k].get("neg") != en_c["AXES"][k].get("neg")
        for k in TRANSLATIONS["AXES"]
    )
    print(f"  {'✅' if axes_ok else '❌'} AXES (8×2) = JA")
    all_ok &= axes_ok

    # ANGLES
    angles_ok = all(
        data["ANGLES"][k][d] != en_c["ANGLES"][k][d]
        for k in TRANSLATIONS["ANGLES"] for d in ("love", "career", "wealth")
    )
    print(f"  {'✅' if angles_ok else '❌'} ANGLES (8×3) = JA")
    all_ok &= angles_ok

    # BALANCED
    bal_ok = (
        data["BALANCED"]["intro"] != en_c["BALANCED"]["intro"]
        and data["BALANCED"]["body"] != en_c["BALANCED"]["body"]
        and all(data["BALANCED"]["angle"][d] != en_c["BALANCED"]["angle"][d]
                for d in ("love", "career", "wealth"))
    )
    print(f"  {'✅' if bal_ok else '❌'} BALANCED (intro/body/angle×3) = JA")
    all_ok &= bal_ok

    # MODE_SECTION_LABEL
    msl_ok = all(data["MODE_SECTION_LABEL"].get(k) != en_c["MODE_SECTION_LABEL"].get(k)
                 for k in ("bond", "work", "money"))
    print(f"  {'✅' if msl_ok else '❌'} MODE_SECTION_LABEL (3) = JA")
    all_ok &= msl_ok

    # 템플릿 6종
    tpl_ok = all(
        data.get(f) != en_c.get(f)
        for f in ("INTRO_TEMPLATE", "CLOSING_TEMPLATE", "DISCLAIMER",
                  "COLLISION_SENTENCE", "COLLISION_2_SENTENCE",
                  "PULL_SENTENCE", "PULL_2_SENTENCE")
    )
    print(f"  {'✅' if tpl_ok else '❌'} 템플릿/CLOSING/DISCLAIMER = JA (placeholder 보존)")
    all_ok &= tpl_ok

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())