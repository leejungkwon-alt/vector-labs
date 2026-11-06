# scripts/diversify_relationship_tips.py
"""
1) 5개 언어 JSON: RELATIONSHIP_CONTENT.<type>에 tips_by_band (low/mid/high) 추가
   - 기존 tip은 그대로 남겨 fallback
2) compatibility_writer.py: 점수대 기반으로 tips_by_band 선택
"""
import json
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

TIPS_BY_BAND = {
    "ko": {
        "romance": {
            "low":  "지금은 서로의 언어가 잘 통하지 않는 시기예요. 감정이 앞서면 오해가 커지니, 한 박자 쉬어가세요.",
            "mid":  "관계가 균형을 찾아가는 단계입니다. 작은 표현이 큰 힘이 되니, 일상의 친절을 쌓아가세요.",
            "high": "지금의 끌림을 당연하게 여기지 마세요. 서로를 향한 호기심이 관계의 온도를 유지합니다.",
        },
        "business": {
            "low":  "업무 스타일 차이가 분명합니다. 역할과 책임을 문서로 명확히 하고, 기대치를 미리 맞추세요.",
            "mid":  "서로의 강점이 다르게 작동합니다. 의사결정 규칙을 정해두면 마찰이 줄어듭니다.",
            "high": "신뢰가 쌓이는 단계입니다. 큰 프로젝트로 확장하기 좋지만, 감정 관리도 잊지 마세요.",
        },
        "friend": {
            "low":  "지금은 거리를 조율할 시기예요. 무리하게 가까워지기보다 각자의 리듬을 존중하세요.",
            "mid":  "함께하는 시간과 혼자 있는 시간의 균형이 중요합니다. 편안함이 신뢰의 뿌리가 됩니다.",
            "high": "오래 갈 우정의 기반이 보입니다. 서로의 성장을 응원하는 관계로 발전할 수 있어요.",
        },
        "family": {
            "low":  "세대 간 기대가 부딪히는 지점입니다. 옳고 그름보다 감정의 이면을 먼저 들여다보세요.",
            "mid":  "건강한 경계를 세우는 것이 관건입니다. 사랑과 개입은 다르다는 걸 서로 배워가야 해요.",
            "high": "서로의 뿌리가 되어주는 관계입니다. 감사함을 자주 표현할수록 결속이 단단해집니다.",
        },
    },
    "en": {
        "romance": {
            "low":  "Your emotional languages aren't syncing right now. Slow down — rushing tends to deepen misunderstandings.",
            "mid":  "You're finding balance. Small gestures matter — invest in daily kindness.",
            "high": "Don't take the pull for granted. Mutual curiosity keeps the temperature alive.",
        },
        "business": {
            "low":  "Your working styles clearly differ. Document roles and align expectations up front.",
            "mid":  "Your strengths play out differently. Setting decision rules reduces friction.",
            "high": "Trust is building. Good time for bigger projects — but keep emotions in check.",
        },
        "friend": {
            "low":  "Time to calibrate distance. Respect each other's rhythm instead of forcing closeness.",
            "mid":  "Balance time together and time apart. Comfort is the root of trust.",
            "high": "The foundation for lasting friendship is visible. You can grow into cheerleaders for each other.",
        },
        "family": {
            "low":  "Generational expectations are colliding. Look underneath the right/wrong to the emotions.",
            "mid":  "Healthy boundaries are the key. Learn that love and intrusion are different.",
            "high": "You're each other's roots. The more you voice gratitude, the stronger the bond.",
        },
    },
    "ja": {
        "romance": {
            "low":  "今は互いの言葉が通じにくい時期。感情が先行すると誤解が深まるので、一歩引いてみて。",
            "mid":  "関係がバランスを見つける段階です。小さな表現が大きな力になるので、日常の優しさを積み重ねて。",
            "high": "今の惹かれ合いを当たり前にしないで。互いへの好奇心が関係の温度を保ちます。",
        },
        "business": {
            "low":  "仕事のスタイルが明確に違います。役割と責任を文書化し、期待値を事前にすり合わせて。",
            "mid":  "強みの発揮の仕方が異なります。意思決定のルールを決めれば摩擦が減ります。",
            "high": "信頼が積み上がる段階。大きなプロジェクトへの拡大に良い時期ですが、感情管理も忘れずに。",
        },
        "friend": {
            "low":  "距離を調整する時期。無理に近づくより、互いのリズムを尊重して。",
            "mid":  "一緒の時間と一人の時間のバランスが大事。心地よさが信頼の根になります。",
            "high": "長く続く友情の基盤が見えます。互いの成長を応援できる関係に発展できます。",
        },
        "family": {
            "low":  "世代間の期待がぶつかる地点。正しさより感情の奥を先に見てください。",
            "mid":  "健全な境界線を引くことが鍵。愛と干渉は違うと互いに学んでいきましょう。",
            "high": "互いの根になる関係。感謝を頻繁に伝えるほど絆が固まります。",
        },
    },
    "zh": {
        "romance": {
            "low":  "目前彼此的语言不太同步。情绪先行容易加深误会，先慢一步。",
            "mid":  "关系正在寻找平衡。小小的表达也很有力量，多积累日常的体贴。",
            "high": "不要把现在的吸引力当作理所当然。对彼此的好奇心维系关系温度。",
        },
        "business": {
            "low":  "工作风格明显不同。把角色与责任写成文档，提前对齐期望。",
            "mid":  "双方强项发挥方式不同。定好决策规则可减少摩擦。",
            "high": "信任在累积。适合扩大项目，但别忘了情绪管理。",
        },
        "friend": {
            "low":  "现在需要调整距离。与其强行亲近，不如尊重彼此节奏。",
            "mid":  "相处与独处的平衡很重要。舒适感是信任的根基。",
            "high": "长久友谊的基础已显现。可以发展为彼此成长的伙伴。",
        },
        "family": {
            "low":  "代际期望在碰撞。先看情感，再看对错。",
            "mid":  "设立健康边界是关键。爱与干涉是不同的。",
            "high": "你们互为彼此的根。多表达感谢，关系更牢固。",
        },
    },
    "es": {
        "romance": {
            "low":  "Sus lenguajes emocionales no están sincronizados. Bajen el ritmo — apurarse profundiza malentendidos.",
            "mid":  "Están encontrando el equilibrio. Los pequeños gestos importan — inviertan en amabilidad diaria.",
            "high": "No den por sentada la atracción. La curiosidad mutua mantiene la temperatura.",
        },
        "business": {
            "low":  "Sus estilos de trabajo difieren claramente. Documenten roles y alineen expectativas.",
            "mid":  "Sus fortalezas se expresan distinto. Reglas claras reducen fricción.",
            "high": "La confianza crece. Buen momento para proyectos grandes, sin descuidar lo emocional.",
        },
        "friend": {
            "low":  "Momento de calibrar la distancia. Respeten el ritmo del otro.",
            "mid":  "El equilibrio entre tiempo juntos y a solas importa. La comodidad es raíz de confianza.",
            "high": "Se ve la base de una amistad duradera. Pueden crecer apoyándose mutuamente.",
        },
        "family": {
            "low":  "Las expectativas generacionales chocan. Miren las emociones antes que lo correcto.",
            "mid":  "Establecer límites sanos es la clave. Amor e intromisión son distintos.",
            "high": "Son las raíces del otro. Expresar gratitud refuerza el vínculo.",
        },
    },
}

def lang_key(p):
    s = p.stem.lower()
    return ("zh" if s.startswith("zh") else "ja" if s.startswith("ja") else
            "es" if s.startswith("es") else "ko" if s.startswith("ko") else
            "en" if s.startswith("en") else None)

# ============ 1. JSON 패치 ============
print("=" * 50)
print("1) 5개 언어 JSON에 tips_by_band 추가")
print("=" * 50)
for f in Path("app/services/content/data").rglob("compatibility.json"):
    lang = lang_key(f)
    if lang not in TIPS_BY_BAND:
        continue
    with open(f, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    rc = data.get("RELATIONSHIP_CONTENT")
    if not isinstance(rc, dict):
        print(f"⚠️ {f.name}: RELATIONSHIP_CONTENT 없음")
        continue
    added = []
    for rtype, bands in TIPS_BY_BAND[lang].items():
        entry = rc.get(rtype, {})
        if "tips_by_band" in entry:
            continue
        entry["tips_by_band"] = bands
        rc[rtype] = entry
        added.append(rtype)
    if added:
        print(f"✅ {f.name}: {added} tips_by_band 추가")
        if APPLY:
            with open(f, "w", encoding="utf-8") as fp:
                json.dump(data, fp, ensure_ascii=False, indent=2)
    else:
        print(f"ℹ️ {f.name}: 이미 추가됨")

# ============ 2. writer.py 패치 ============
print("\n" + "=" * 50)
print("2) writer.py: 점수대 기반 relationship_advice 선택")
print("=" * 50)
WRITER = Path("app/services/compatibility_writer.py")
if WRITER.exists():
    txt = WRITER.read_text(encoding="utf-8")
    orig = txt

    old = '''    rel_pack = pack.get("RELATIONSHIP_CONTENT", {}).get(relationship_type, {})
    relationship_advice = rel_pack.get("tip", "")'''

    new = '''    rel_pack = pack.get("RELATIONSHIP_CONTENT", {}).get(relationship_type, {})
    tips_by_band = rel_pack.get("tips_by_band") or {}
    try:
        _s = (float(overall["score"]) + 1) / 2 * 100
    except (TypeError, ValueError):
        _s = 50.0
    if _s < 45:
        _band = "low"
    elif _s < 65:
        _band = "mid"
    else:
        _band = "high"
    relationship_advice = tips_by_band.get(_band) or rel_pack.get("tip", "")'''

    if old in txt:
        txt = txt.replace(old, new, 1)
        print("✅ writer.py: 점수대 기반 tip 선택 로직 추가")
        if APPLY:
            WRITER.write_text(txt, encoding="utf-8")
    else:
        print("❌ writer.py: 패턴 불일치. 수동 확인 필요")

print()
if not APPLY:
    print("🧪 미리보기.  적용: python scripts/diversify_relationship_tips.py --apply")
else:
    print("🎉 패치 완료. 다음:")
    print("   .\\deploy.ps1")