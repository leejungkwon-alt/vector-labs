# scripts/diversify_neutral.py
"""
1) 5개 언어 JSON: OVERALL_CONTENT에 NEUTRAL_VARIANTS 배열 추가 (3개)
2) compatibility_writer.py: NEUTRAL일 때 score 기반 variant 선택
"""
import json
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

VARIANTS = {
    "ko": [
        {"headline": "에너지가 다른 방향을 가리킵니다.",
         "body": "두 사람의 리듬과 반응 속도가 다릅니다. 억지로 맞추려 하면 지치기 쉬우니, 서로의 템포를 인정하는 것부터 시작해 보세요. 다름이 곧 위협은 아닙니다."},
        {"headline": "익숙함과 새로움이 교차합니다.",
         "body": "같은 상황에서도 다르게 반응하는 조합입니다. 그 차이가 때로는 피로가 되고, 때로는 매력이 됩니다. 중요한 순간에 누가 먼저 웃어 주는지가 관계의 온도를 결정합니다."},
        {"headline": "결정적 순간의 반 발짝입니다.",
         "body": "구조적으로 큰 충돌은 없지만, 저절로 완성되지도 않습니다. 갈림길에서 두 사람이 서로를 향해 반 발짝씩 움직이는지가 관건입니다. 쌓아온 신뢰가 그 순간에 힘을 발휘합니다."},
    ],
    "en": [
        {"headline": "Your energies point in different directions.",
         "body": "Your rhythms and reaction speeds differ. Forcing alignment will tire you out — start by acknowledging each other's tempo. Difference is not a threat."},
        {"headline": "A mix of the familiar and the new.",
         "body": "You respond differently to the same situations. That gap can feel exhausting at times and magnetic at others. Who smiles first in pivotal moments often sets the temperature of the relationship."},
        {"headline": "Half a step at decisive moments.",
         "body": "No major structural clash, but it won't complete itself. The key is whether you both take half a step toward the other at crossroads. Trust you've built shows its strength in those moments."},
    ],
    "ja": [
        {"headline": "エネルギーが異なる方向を向いています。",
         "body": "二人のリズムと反応の速さが違います。無理に合わせようとすると疲れやすいので、互いのテンポを認めることから始めましょう。違いは脅威ではありません。"},
        {"headline": "慣れと新しさが交差しています。",
         "body": "同じ状況でも反応が異なる組み合わせです。その差は時に疲れを、時に魅力を生みます。決定的な瞬間にどちらが先に笑うかが関係の温度を決めます。"},
        {"headline": "決定的な瞬間の半歩です。",
         "body": "構造的な大きな衝突はありませんが、自然に完成するものでもありません。分岐点で互いに半歩ずつ歩み寄れるかが鍵です。積み重ねた信頼がその瞬間に力を発揮します。"},
    ],
    "zh": [
        {"headline": "能量指向不同的方向。",
         "body": "两人的节奏与反应速度不同。勉强对齐容易疲惫，不妨先承认彼此的节奏。差异并非威胁。"},
        {"headline": "熟悉与新鲜的交错。",
         "body": "面对相同情境反应各异的组合。这种差异有时令人疲惫，有时又充满吸引力。关键时刻谁先微笑，往往决定关系的温度。"},
        {"headline": "决定性时刻的半步。",
         "body": "没有大的结构性冲突，但也不会自然完成。关键在于岔路口你们是否都朝对方迈出半步。过往建立的信任会在那一刻发挥力量。"},
    ],
    "es": [
        {"headline": "Sus energías apuntan en direcciones distintas.",
         "body": "Sus ritmos y tiempos de reacción difieren. Forzar la alineación cansa; empiecen por reconocer el tempo del otro. La diferencia no es una amenaza."},
        {"headline": "Mezcla de lo familiar y lo nuevo.",
         "body": "Responden diferente ante las mismas situaciones. Esa brecha a veces agota, a veces atrae. Quién sonríe primero en los momentos clave suele marcar la temperatura de la relación."},
        {"headline": "Medio paso en los momentos decisivos.",
         "body": "Sin choques estructurales importantes, pero tampoco se completa solo. La clave es si ambos dan medio paso hacia el otro en las encrucijadas. La confianza construida se nota ahí."},
    ],
}

def lang_key(p):
    s = p.stem.lower()
    return ("zh" if s.startswith("zh") else "ja" if s.startswith("ja") else
            "es" if s.startswith("es") else "ko" if s.startswith("ko") else
            "en" if s.startswith("en") else None)

# ============ 1. JSON 패치 ============
print("=" * 50)
print("1) 5개 언어 JSON에 NEUTRAL_VARIANTS 추가")
print("=" * 50)
for f in Path("app/services/content/data").rglob("compatibility.json"):
    lang = lang_key(f)
    if lang not in VARIANTS:
        continue
    with open(f, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    oc = data.get("OVERALL_CONTENT")
    if not isinstance(oc, dict):
        print(f"⚠️ {f.name}: OVERALL_CONTENT 없음")
        continue
    if "NEUTRAL_VARIANTS" in oc:
        print(f"ℹ️ {f.name}: 이미 NEUTRAL_VARIANTS 있음")
        continue
    oc["NEUTRAL_VARIANTS"] = VARIANTS[lang]
    print(f"✅ {f.name}: NEUTRAL_VARIANTS 3개 추가")
    if APPLY:
        with open(f, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)

# ============ 2. writer.py 패치 ============
print("\n" + "=" * 50)
print("2) compatibility_writer.py NEUTRAL variant 선택 로직")
print("=" * 50)
WRITER = Path("app/services/compatibility_writer.py")
if WRITER.exists():
    txt = WRITER.read_text(encoding="utf-8")
    orig = txt

    old = '''    overall = compat["overall"]
    _overall_all = pack.get("OVERALL_CONTENT", {})
    overall_content = _overall_all.get(overall["grade"]) or _overall_all.get("NEUTRAL", {})'''

    new = '''    overall = compat["overall"]
    _overall_all = pack.get("OVERALL_CONTENT", {})

    # NEUTRAL 등급이면 score 기반으로 variants 중 하나 선택 (반복 방지)
    if overall["grade"] == "NEUTRAL" and _overall_all.get("NEUTRAL_VARIANTS"):
        variants = _overall_all["NEUTRAL_VARIANTS"]
        try:
            # score: -1.0 ~ 1.0 → 0~100으로 변환
            s = (float(overall["score"]) + 1) / 2 * 100
        except (TypeError, ValueError):
            s = 50.0
        n = len(variants)
        idx = min(n - 1, max(0, int(s // (100.0 / n))))
        overall_content = variants[idx]
    else:
        overall_content = _overall_all.get(overall["grade"]) or _overall_all.get("NEUTRAL", {})'''

    if old in txt:
        txt = txt.replace(old, new, 1)
        print("✅ writer.py: NEUTRAL score 기반 variant 선택 로직 추가")
        if APPLY:
            WRITER.write_text(txt, encoding="utf-8")
    else:
        print("❌ writer.py: 패턴 불일치. 수동 확인 필요")

print()
if not APPLY:
    print("🧪 미리보기.  적용: python scripts/diversify_neutral.py --apply")
else:
    print("🎉 패치 완료. 다음:")
    print("   .\\deploy.ps1")