# scripts/force_5_variants.py
"""JSON NEUTRAL_VARIANTS를 5개로 강제 덮어쓰기 (3개든 5개든 상관없이)."""
import json
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

# 5개 variants (기존과 동일)
VARIANTS_5 = {
    "ko": [
        {"headline": "서로의 결이 꽤 다릅니다.", "body": "지금은 같은 방향을 보기 어려울 수 있습니다. 억지로 맞추기보다 각자의 속도를 인정하고, 신뢰를 쌓는 데 집중하세요."},
        {"headline": "에너지가 다른 방향을 가리킵니다.", "body": "두 사람의 리듬과 반응 속도가 다릅니다. 억지로 맞추려 하면 지치기 쉬우니, 서로의 템포를 인정하는 것부터 시작해 보세요."},
        {"headline": "익숙함과 새로움이 교차합니다.", "body": "같은 상황에서도 다르게 반응하는 조합입니다. 그 차이가 때로는 피로가 되고, 때로는 매력이 됩니다. 중요한 순간에 누가 먼저 웃어 주는지가 관계의 온도를 결정합니다."},
        {"headline": "결정적 순간의 반 발짝입니다.", "body": "구조적으로 큰 충돌은 없지만, 저절로 완성되지도 않습니다. 갈림길에서 두 사람이 서로를 향해 반 발짝씩 움직이는지가 관건입니다."},
        {"headline": "서로의 빛을 밝혀주는 관계입니다.", "body": "두 사람이 가진 고유한 기질이 만나 시너지를 냅니다. 함께할 때 서로의 장점이 더 선명해지고, 어려운 순간에도 힘이 됩니다."},
    ],
    "en": [
        {"headline": "Your textures differ considerably.", "body": "Seeing eye to eye may be hard right now. Focus on acknowledging each other's pace and building trust."},
        {"headline": "Your energies point in different directions.", "body": "Your rhythms and reaction speeds differ. Forcing alignment will tire you out — start by acknowledging each other's tempo."},
        {"headline": "A mix of the familiar and the new.", "body": "You respond differently to the same situations. That gap can feel exhausting at times and magnetic at others."},
        {"headline": "Half a step at decisive moments.", "body": "No major structural clash, but it won't complete itself. The key is whether you both take half a step toward the other."},
        {"headline": "A relationship that lights each other up.", "body": "Your unique qualities create synergy. Together, your strengths become clearer."},
    ],
    "ja": [
        {"headline": "互いの質感がかなり異なります。", "body": "今は同じ方向を見るのが難しいかもしれません。無理に合わせるより、互いのペースを認めて信頼を築くことに集中を。"},
        {"headline": "エネルギーが異なる方向を向いています。", "body": "二人のリズムと反応の速さが違います。互いのテンポを認めることから始めましょう。"},
        {"headline": "慣れと新しさが交差しています。", "body": "同じ状況でも反応が異なる組み合わせです。その差は時に疲れを、時に魅力を生みます。"},
        {"headline": "決定的な瞬間の半歩です。", "body": "構造的な大きな衝突はありませんが、自然に完成するものでもありません。分岐点で互いに半歩ずつ歩み寄れるかが鍵です。"},
        {"headline": "互いの光を輝かせる関係です。", "body": "二人の独自の資質が出会いシナジーを生みます。一緒にいる時、互いの強みがより鮮明になります。"},
    ],
    "zh_cn": [
        {"headline": "彼此的质感差异较大。", "body": "目前可能难以看到同一方向。与其勉强配合，不如承认彼此的节奏。"},
        {"headline": "能量指向不同的方向。", "body": "两人的节奏与反应速度不同。勉强对齐容易疲惫，不妨先承认彼此的节奏。"},
        {"headline": "熟悉与新鲜的交错。", "body": "面对相同情境反应各异的组合。这种差异有时令人疲惫，有时又充满吸引力。"},
        {"headline": "决定性时刻的半步。", "body": "没有大的结构性冲突，但也不会自然完成。关键在于岔路口你们是否都朝对方迈出半步。"},
        {"headline": "照亮彼此的关系。", "body": "两人独特的品质相遇产生协同效应。在一起时，双方的强项会更加鲜明。"},
    ],
    "es": [
        {"headline": "Sus texturas difieren bastante.", "body": "Ver las cosas igual puede ser difícil ahora. Concéntrense en reconocer el ritmo del otro."},
        {"headline": "Sus energías apuntan en direcciones distintas.", "body": "Sus ritmos y tiempos de reacción difieren. Forzar la alineación cansa."},
        {"headline": "Mezcla de lo familiar y lo nuevo.", "body": "Responden diferente ante las mismas situaciones. Esa brecha a veces agota, a veces atrae."},
        {"headline": "Medio paso en los momentos decisivos.", "body": "Sin choques estructurales importantes, pero tampoco se completa solo. La clave es dar medio paso en las encrucijadas."},
        {"headline": "Una relación que se ilumina mutuamente.", "body": "Sus cualidades únicas crean sinergia. Juntos, sus fortalezas se vuelven más claras."},
    ],
}

def lang_key(p):
    raw = p.parent.name.lower()
    return "zh_cn" if raw.startswith("zh") else raw

print("=" * 55)
print("NEUTRAL_VARIANTS 5개로 강제 덮어쓰기")
print("=" * 55)
for f in Path("app/services/content/data").rglob("compatibility.json"):
    lang = lang_key(f)
    if lang not in VARIANTS_5:
        continue
    with open(f, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    oc = data.get("OVERALL_CONTENT")
    if not isinstance(oc, dict):
        print(f"⚠️ {f}: OVERALL_CONTENT 없음")
        continue
    before = len(oc.get("NEUTRAL_VARIANTS", []))
    oc["NEUTRAL_VARIANTS"] = VARIANTS_5[lang]
    after = len(oc["NEUTRAL_VARIANTS"])
    print(f"✅ {lang}: {before}개 → {after}개")
    if APPLY:
        with open(f, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)

print()
if not APPLY:
    print("🧪 미리보기. 적용: python scripts/force_5_variants.py --apply")
else:
    print("🎉 완료. 다음:")
    print("   .\\deploy.ps1    ← 반드시 실행!")