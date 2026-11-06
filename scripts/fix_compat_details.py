# scripts/fix_compat_details.py
"""
1) compatibility.tsx: axis.shared?.length, axis.breakdown?.length 로 옵셔널 체이닝 추가 (콘솔 에러 해결)
2) JSON: NEUTRAL_VARIANTS를 3개 → 5개로 확장 (점수대 세분화)
3) writer.py: 5개 구간(0~20, 20~40, 40~60, 60~80, 80~100)에 맞게 인덱스 계산 수정
"""
import json
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

# ==========================================
# 1) 프론트엔드 콘솔 에러 해결
# ==========================================
print("=" * 50)
print("1) frontend: optional chaining 추가")
print("=" * 50)
TSX = Path("frontend/app/(tabs)/compatibility.tsx")
if TSX.exists():
    txt = TSX.read_text(encoding="utf-8")
    orig = txt
    # .length 앞에 ?. 추가
    txt = re.sub(r'([a-zA-Z_]+)\.shared\.length', r'\1.shared?.length', txt)
    txt = re.sub(r'([a-zA-Z_]+)\.breakdown\.length', r'\1.breakdown?.length', txt)
    
    if txt != orig:
        print("  ✅ .shared / .breakdown 옵셔널 체이닝 적용")
        if APPLY:
            TSX.write_text(txt, encoding="utf-8")
    else:
        print("  ℹ️ 변경할 패턴 없음 (이미 적용됨)")

# ==========================================
# 2) JSON: NEUTRAL_VARIANTS 5개로 확장
# ==========================================
print("\n" + "=" * 50)
print("2) JSON: NEUTRAL_VARIANTS 5개로 확장")
print("=" * 50)

# 기존 3개에 2개를 추가 (매우 낮음, 매우 높음)
NEW_VARIANTS = {
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
        {"headline": "A relationship that lights each other up.", "body": "Your unique qualities create synergy. Together, your strengths become clearer and support you through tough moments."},
    ],
    "ja": [
        {"headline": "互いの質感がかなり異なります。", "body": "今は同じ方向を見るのが難しいかもしれません。無理に合わせるより、互いのペースを認めて信頼を築くことに集中を。"},
        {"headline": "エネルギーが異なる方向を向いています。", "body": "二人のリズムと反応の速さが違います。無理に合わせようとすると疲れやすいので、互いのテンポを認めることから始めましょう。"},
        {"headline": "慣れと新しさが交差しています。", "body": "同じ状況でも反応が異なる組み合わせです。その差は時に疲れを、時に魅力を生みます。"},
        {"headline": "決定的な瞬間の半歩です。", "body": "構造的な大きな衝突はありませんが、自然に完成するものでもありません。分岐点で互いに半歩ずつ歩み寄れるかが鍵です。"},
        {"headline": "互いの光を輝かせる関係です。", "body": "二人の独自の資質が出会いシナジーを生みます。一緒にいる時、互いの強みがより鮮明になります。"},
    ],
    "zh_cn": [
        {"headline": "彼此的质感差异较大。", "body": "目前可能难以看到同一方向。与其勉强配合，不如承认彼此的节奏，专注于建立信任。"},
        {"headline": "能量指向不同的方向。", "body": "两人的节奏与反应速度不同。勉强对齐容易疲惫，不妨先承认彼此的节奏。"},
        {"headline": "熟悉与新鲜的交错。", "body": "面对相同情境反应各异的组合。这种差异有时令人疲惫，有时又充满吸引力。"},
        {"headline": "决定性时刻的半步。", "body": "没有大的结构性冲突，但也不会自然完成。关键在于岔路口你们是否都朝对方迈出半步。"},
        {"headline": "照亮彼此的关系。", "body": "两人独特的品质相遇产生协同效应。在一起时，双方的强项会更加鲜明。"},
    ],
    "es": [
        {"headline": "Sus texturas difieren bastante.", "body": "Ver las cosas igual puede ser difícil ahora. Concéntrense en reconocer el ritmo del otro y construir confianza."},
        {"headline": "Sus energías apuntan en direcciones distintas.", "body": "Sus ritmos y tiempos de reacción difieren. Forzar la alineación cansa."},
        {"headline": "Mezcla de lo familiar y lo nuevo.", "body": "Responden diferente ante las mismas situaciones. Esa brecha a veces agota, a veces atrae."},
        {"headline": "Medio paso en los momentos decisivos.", "body": "Sin choques estructurales importantes, pero tampoco se completa solo. La clave es dar medio paso en las encrucijadas."},
        {"headline": "Una relación que se ilumina mutuamente.", "body": "Sus cualidades únicas crean sinergia. Juntos, sus fortalezas se vuelven más claras."},
    ],
}

def lang_key(p):
    raw = p.parent.name.lower()
    return "zh_cn" if raw.startswith("zh") else raw

for f in Path("app/services/content/data").rglob("compatibility.json"):
    lang = lang_key(f)
    if lang not in NEW_VARIANTS:
        continue
    with open(f, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    oc = data.get("OVERALL_CONTENT")
    if not isinstance(oc, dict):
        continue
    oc["NEUTRAL_VARIANTS"] = NEW_VARIANTS[lang] # 덮어쓰기
    print(f"  ✅ {lang}: NEUTRAL_VARIANTS 5개로 업데이트")
    if APPLY:
        with open(f, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)

# ==========================================
# 3) writer.py: 5개 구간에 맞게 인덱스 계산
# ==========================================
print("\n" + "=" * 50)
print("3) writer.py: 5개 구간에 맞게 인덱스 계산")
print("=" * 50)
WRITER = Path("app/services/compatibility_writer.py")
if WRITER.exists():
    txt = WRITER.read_text(encoding="utf-8")
    # 기존 int(s100 // (100.0 / n)) 로직을 5등분으로 명시적 변경
    old_logic = 'idx = min(n - 1, max(0, int(s100 // (100.0 / n))))'
    new_logic = 'idx = min(n - 1, max(0, int(s100 // (100.0 / n))))  # 5개일 경우 20점 단위로 나뉨'
    if old_logic in txt:
        txt = txt.replace(old_logic, new_logic, 1)
        print("  ✅ writer.py 인덱스 계산 확인 (이미 n 등분 로직이므로 수정 불필요)")
        # n=5이면 100/5 = 20. 0-19, 20-39, 40-59, 60-79, 80-100 으로 자동 분할됨!
    if APPLY:
        WRITER.write_text(txt, encoding="utf-8")

print()
if not APPLY:
    print("🧪 미리보기. 적용: python scripts/fix_compat_details.py --apply")
else:
    print("🎉 패치 완료. 다음:")
    print("   .\\deploy.ps1  (백엔드 배포)")
    print("   git add frontend/app/(tabs)/compatibility.tsx")
    print("   git commit -m 'fix: compatibility console error and variants'")
    print("   git push origin main  (프론트엔드 배포)")