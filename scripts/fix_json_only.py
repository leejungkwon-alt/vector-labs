# scripts/fix_json_only.py
"""JSON만 패치. 부모 폴더명(ko/en/ja/zh_cn/es)을 언어로 사용. 디버그 출력 포함."""
import json
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

NEUTRAL_VARIANTS = {
    "ko": [
        {"headline": "에너지가 다른 방향을 가리킵니다.", "body": "두 사람의 리듬과 반응 속도가 다릅니다. 억지로 맞추려 하면 지치기 쉬우니, 서로의 템포를 인정하는 것부터 시작해 보세요. 다름이 곧 위협은 아닙니다."},
        {"headline": "익숙함과 새로움이 교차합니다.", "body": "같은 상황에서도 다르게 반응하는 조합입니다. 그 차이가 때로는 피로가 되고, 때로는 매력이 됩니다. 중요한 순간에 누가 먼저 웃어 주는지가 관계의 온도를 결정합니다."},
        {"headline": "결정적 순간의 반 발짝입니다.", "body": "구조적으로 큰 충돌은 없지만, 저절로 완성되지도 않습니다. 갈림길에서 두 사람이 서로를 향해 반 발짝씩 움직이는지가 관건입니다. 쌓아온 신뢰가 그 순간에 힘을 발휘합니다."},
    ],
    "en": [
        {"headline": "Your energies point in different directions.", "body": "Your rhythms and reaction speeds differ. Forcing alignment will tire you out — start by acknowledging each other's tempo. Difference is not a threat."},
        {"headline": "A mix of the familiar and the new.", "body": "You respond differently to the same situations. That gap can feel exhausting at times and magnetic at others. Who smiles first in pivotal moments often sets the temperature."},
        {"headline": "Half a step at decisive moments.", "body": "No major structural clash, but it won't complete itself. The key is whether you both take half a step toward the other at crossroads."},
    ],
    "ja": [
        {"headline": "エネルギーが異なる方向を向いています。", "body": "二人のリズムと反応の速さが違います。無理に合わせようとすると疲れやすいので、互いのテンポを認めることから始めましょう。"},
        {"headline": "慣れと新しさが交差しています。", "body": "同じ状況でも反応が異なる組み合わせです。その差は時に疲れを、時に魅力を生みます。決定的な瞬間にどちらが先に笑うかが関係の温度を決めます。"},
        {"headline": "決定的な瞬間の半歩です。", "body": "構造的な大きな衝突はありませんが、自然に完成するものでもありません。分岐点で互いに半歩ずつ歩み寄れるかが鍵です。"},
    ],
    "zh_cn": [
        {"headline": "能量指向不同的方向。", "body": "两人的节奏与反应速度不同。勉强对齐容易疲惫，不妨先承认彼此的节奏。差异并非威胁。"},
        {"headline": "熟悉与新鲜的交错。", "body": "面对相同情境反应各异的组合。这种差异有时令人疲惫，有时又充满吸引力。关键时刻谁先微笑，往往决定关系的温度。"},
        {"headline": "决定性时刻的半步。", "body": "没有大的结构性冲突，但也不会自然完成。关键在于岔路口你们是否都朝对方迈出半步。"},
    ],
    "es": [
        {"headline": "Sus energías apuntan en direcciones distintas.", "body": "Sus ritmos y tiempos de reacción difieren. Forzar la alineación cansa; empiecen por reconocer el tempo del otro."},
        {"headline": "Mezcla de lo familiar y lo nuevo.", "body": "Responden diferente ante las mismas situaciones. Esa brecha a veces agota, a veces atrae. Quién sonríe primero en los momentos clave marca la temperatura."},
        {"headline": "Medio paso en los momentos decisivos.", "body": "Sin choques estructurales importantes, pero tampoco se completa solo. La clave es si ambos dan medio paso hacia el otro en las encrucijadas."},
    ],
}

TIPS_BY_BAND = {
    "ko": {
        "romance": {"low": "지금은 서로의 언어가 잘 통하지 않는 시기예요. 감정이 앞서면 오해가 커지니, 한 박자 쉬어가세요.", "mid": "관계가 균형을 찾아가는 단계입니다. 작은 표현이 큰 힘이 되니, 일상의 친절을 쌓아가세요.", "high": "지금의 끌림을 당연하게 여기지 마세요. 서로를 향한 호기심이 관계의 온도를 유지합니다."},
        "business": {"low": "업무 스타일 차이가 분명합니다. 역할과 책임을 문서로 명확히 하고, 기대치를 미리 맞추세요.", "mid": "서로의 강점이 다르게 작동합니다. 의사결정 규칙을 정해두면 마찰이 줄어듭니다.", "high": "신뢰가 쌓이는 단계입니다. 큰 프로젝트로 확장하기 좋지만, 감정 관리도 잊지 마세요."},
        "friend": {"low": "지금은 거리를 조율할 시기예요. 무리하게 가까워지기보다 각자의 리듬을 존중하세요.", "mid": "함께하는 시간과 혼자 있는 시간의 균형이 중요합니다. 편안함이 신뢰의 뿌리가 됩니다.", "high": "오래 갈 우정의 기반이 보입니다. 서로의 성장을 응원하는 관계로 발전할 수 있어요."},
        "family": {"low": "세대 간 기대가 부딪히는 지점입니다. 옳고 그름보다 감정의 이면을 먼저 들여다보세요.", "mid": "건강한 경계를 세우는 것이 관건입니다. 사랑과 개입은 다르다는 걸 서로 배워가야 해요.", "high": "서로의 뿌리가 되어주는 관계입니다. 감사함을 자주 표현할수록 결속이 단단해집니다."},
    },
    "en": {
        "romance": {"low": "Your emotional languages aren't syncing. Slow down — rushing deepens misunderstandings.", "mid": "You're finding balance. Small gestures matter — invest in daily kindness.", "high": "Don't take the pull for granted. Mutual curiosity keeps the temperature alive."},
        "business": {"low": "Working styles clearly differ. Document roles and align expectations up front.", "mid": "Your strengths play out differently. Decision rules reduce friction.", "high": "Trust is building. Good time for bigger projects — keep emotions in check too."},
        "friend": {"low": "Time to calibrate distance. Respect each other's rhythm instead of forcing closeness.", "mid": "Balance together-time and apart-time. Comfort is the root of trust.", "high": "Lasting-friendship foundation is visible. Grow into cheerleaders for each other."},
        "family": {"low": "Generational expectations are colliding. Look under the right/wrong to the emotions.", "mid": "Healthy boundaries are key. Learn that love and intrusion are different.", "high": "You're each other's roots. Voicing gratitude strengthens the bond."},
    },
    "ja": {
        "romance": {"low": "今は互いの言葉が通じにくい時期。感情が先行すると誤解が深まるので、一歩引いてみて。", "mid": "関係がバランスを見つける段階。小さな表現が大きな力になるので、日常の優しさを積み重ねて。", "high": "今の惹かれ合いを当たり前にしないで。互いへの好奇心が関係の温度を保ちます。"},
        "business": {"low": "仕事のスタイルが明確に違います。役割と責任を文書化し、期待値を事前にすり合わせて。", "mid": "強みの発揮の仕方が異なります。意思決定のルールを決めれば摩擦が減ります。", "high": "信頼が積み上がる段階。大きなプロジェクトへの拡大に良い時期。"},
        "friend": {"low": "距離を調整する時期。無理に近づくより、互いのリズムを尊重して。", "mid": "一緒の時間と一人の時間のバランスが大事。心地よさが信頼の根になります。", "high": "長く続く友情の基盤が見えます。互いの成長を応援できる関係に発展できます。"},
        "family": {"low": "世代間の期待がぶつかる地点。正しさより感情の奥を先に見てください。", "mid": "健全な境界線を引くことが鍵。愛と干渉は違うと互いに学んでいきましょう。", "high": "互いの根になる関係。感謝を頻繁に伝えるほど絆が固まります。"},
    },
    "zh_cn": {
        "romance": {"low": "目前彼此的语言不太同步。情绪先行容易加深误会，先慢一步。", "mid": "关系正在寻找平衡。小小的表达也很有力量，多积累日常的体贴。", "high": "不要把吸引力当作理所当然。对彼此的好奇心维系关系温度。"},
        "business": {"low": "工作风格明显不同。把角色与责任写成文档，提前对齐期望。", "mid": "双方强项发挥方式不同。定好决策规则可减少摩擦。", "high": "信任在累积。适合扩大项目，但别忘了情绪管理。"},
        "friend": {"low": "需要调整距离。与其强行亲近，不如尊重彼此节奏。", "mid": "相处与独处的平衡很重要。舒适感是信任的根基。", "high": "长久友谊的基础已显现。可以发展为彼此成长的伙伴。"},
        "family": {"low": "代际期望在碰撞。先看情感，再看对错。", "mid": "设立健康边界是关键。爱与干涉是不同的。", "high": "你们互为彼此的根。多表达感谢，关系更牢固。"},
    },
    "es": {
        "romance": {"low": "Sus lenguajes emocionales no están sincronizados. Bajen el ritmo.", "mid": "Están encontrando el equilibrio. Los pequeños gestos importan.", "high": "No den por sentada la atracción. La curiosidad mutua mantiene la temperatura."},
        "business": {"low": "Sus estilos difieren. Documenten roles y alineen expectativas.", "mid": "Sus fortalezas se expresan distinto. Reglas claras reducen fricción.", "high": "La confianza crece. Buen momento para proyectos grandes."},
        "friend": {"low": "Momento de calibrar la distancia. Respeten el ritmo del otro.", "mid": "El equilibrio entre juntos y solos importa. La comodidad es raíz de confianza.", "high": "Base de una amistad duradera. Pueden crecer apoyándose."},
        "family": {"low": "Expectativas generacionales chocan. Miren las emociones antes que lo correcto.", "mid": "Establecer límites sanos es la clave. Amor e intromisión son distintos.", "high": "Son las raíces del otro. Expresar gratitud refuerza el vínculo."},
    },
}

# ========== FILES SCAN ==========
print("=" * 60)
print("FILES SCAN")
print("=" * 60)
all_files = list(Path("app/services/content/data").rglob("compatibility.json"))
print(f"Found {len(all_files)} compatibility.json files:")
for f in all_files:
    print(f"  {f}")
    print(f"    parent.name = '{f.parent.name}'  → lang = '{f.parent.name.lower()}'")

# ========== PATCH ==========
print("\n" + "=" * 60)
print("PATCH")
print("=" * 60)

patched = 0
for f in all_files:
    raw = f.parent.name.lower()
    lang = "zh_cn" if raw.startswith("zh") else raw
    if lang not in NEUTRAL_VARIANTS:
        print(f"⚠️ Skip {f}: lang '{lang}' not recognized")
        continue

    print(f"\n📂 {f} (lang={lang})")
    with open(f, "r", encoding="utf-8") as fp:
        data = json.load(fp)

    print(f"  Top keys: {list(data.keys())}")
    oc = data.get("OVERALL_CONTENT")
    if not isinstance(oc, dict):
        print(f"  ❌ OVERALL_CONTENT not a dict")
        continue
    print(f"  OVERALL_CONTENT keys: {list(oc.keys())}")

    changed = False
    if "NEUTRAL_VARIANTS" not in oc:
        oc["NEUTRAL_VARIANTS"] = NEUTRAL_VARIANTS[lang]
        changed = True
        print(f"  ✅ NEUTRAL_VARIANTS added")
    else:
        print(f"  ℹ️ NEUTRAL_VARIANTS already exists")

    rc = data.get("RELATIONSHIP_CONTENT")
    if isinstance(rc, dict):
        for rtype, bands in TIPS_BY_BAND[lang].items():
            entry = rc.get(rtype, {})
            if "tips_by_band" not in entry:
                entry["tips_by_band"] = bands
                rc[rtype] = entry
                changed = True
                print(f"  ✅ tips_by_band added to {rtype}")

    if changed and APPLY:
        with open(f, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)
        print(f"  💾 SAVED")
        patched += 1

print(f"\n{'=' * 60}")
if not APPLY:
    print("🧪 미리보기. 적용: python scripts/fix_json_only.py --apply")
else:
    print(f"🎉 {patched}개 파일 저장됨.")
    print("   다음: Get-Content 으로 확인 후 .\\deploy.ps1")