# scripts/template_combination.py
"""
각 등급별 intro/body 조합으로 반복 해소.
- 3 intros × 3 bodies = 9 조합 per grade
- Deterministic hash (score + axes + relationship_type)
- 기존 NEUTRAL_VARIANTS는 fallback
"""
import json
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

TEMPLATES = {
    "ko": {
        "PEAK": {
            "intros": ["구조적으로 드문 케미입니다.", "네 축이 유난히 정렬된 조합입니다.", "서로의 결이 자연스럽게 맞물리는 드문 인연입니다."],
            "bodies": [
                "아무것도 보장하지는 않지만, 이 관계는 대부분의 관계보다 더 많은 것을 담을 수 있습니다. 서로의 가능성을 함께 펼쳐갈 수 있는 흔치 않은 바탕이 있습니다.",
                "흔한 조합이 아니에요. 시간이 흐르며 서로를 더 깊이 이해할 수 있는 가능성이 큽니다. 이 인연을 함부로 다루지 않는다면 오래 남을 관계입니다.",
                "구조가 두 사람을 뒷받침합니다. 지금의 신뢰를 쌓아가면 어떤 바람에도 흔들리지 않는 관계가 됩니다.",
            ],
        },
        "FAVORABLE": {
            "intros": ["함께 자랄 수 있는 조합입니다.", "서로에게 좋은 자극이 되는 사이입니다.", "구조가 우호적이라 서로를 통해 성장합니다."],
            "bodies": [
                "저절로 되는 관계는 아니지만, 구조가 뒤에서 받쳐줍니다. 두 사람이 느끼는 마찰은 파괴가 아니라 생산적인 종류예요.",
                "쉽게 무너지지 않는 관계예요. 서로 다른 점이 오히려 대화의 물꼬가 됩니다.",
                "서로의 다름을 이해하려는 노력만 있으면, 관계는 시간이 지날수록 깊어집니다.",
            ],
        },
        "NEUTRAL": {
            "intros": ["익숙함과 새로움이 교차합니다.", "지금은 서로의 리듬을 맞춰가는 시기입니다.", "두 사람은 서로 다른 매력으로 서로를 자극합니다."],
            "bodies": [
                "같은 상황에서도 다르게 반응하는 조합입니다. 그 차이가 때로는 피로가 되고, 때로는 매력이 됩니다. 중요한 순간에 누가 먼저 웃어 주는지가 관계의 온도를 결정합니다.",
                "억지로 맞추기보다 각자의 속도를 인정할 때 관계가 깊어집니다. 쌓아온 신뢰가 어려운 순간에 힘을 발휘합니다.",
                "서로의 차이를 인정하는 순간, 관계는 예상치 못한 방향으로 성장합니다. 다정하고 따뜻한 소통이 오래가는 비결입니다.",
            ],
        },
        "CAUTION": {
            "intros": ["많은 것을 요구하는 조합입니다.", "지금은 실질적인 마찰이 있는 시기입니다.", "솔직한 대화가 특히 필요한 관계입니다."],
            "bodies": [
                "실질적인 마찰이 있습니다. 헤어지라는 뜻은 아니고, 일찍, 자주, 솔직하게 말하라는 뜻이에요.",
                "서로의 차이를 회피하면 문제가 커집니다. 불편한 대화를 피하지 마세요.",
                "감정이 앞설 때일수록 한 박자 쉬어가세요. 신뢰를 쌓는 데는 시간이 필요합니다.",
            ],
        },
        "CHALLENGING": {
            "intros": ["모든 것을 요구하는 조합입니다.", "구조적으로 어려운 관계입니다.", "두 사람 모두 의식적으로 노력해야 하는 사이입니다."],
            "bodies": [
                "구조가 두 사람을 거스릅니다. 결과가 정해진 건 아니지만, 대부분의 날에 두 사람 모두 의식적으로 의지를 내야 합니다.",
                "쉬운 관계가 아닙니다. 하지만 서로에 대한 진심이 있다면, 이 어려움을 함께 넘어갈 수 있습니다.",
                "지금의 노력이 관계의 미래를 결정합니다. 작은 배려 하나하나가 큰 차이를 만듭니다.",
            ],
        },
    },
    "en": {
        "PEAK": {
            "intros": ["A structurally rare chemistry.", "All four axes unusually aligned.", "A rare connection where your shapes naturally interlock."],
            "bodies": [
                "Nothing is guaranteed, but this bond can hold more than most. You have a rare foundation to unfold each other's potential together.",
                "Not a common pairing. There's a strong chance you'll come to understand each other more deeply over time. Handle this bond carefully, and it lasts.",
                "Structure backs you both. Build trust now, and this becomes a relationship that won't sway in any storm.",
            ],
        },
        "FAVORABLE": {
            "intros": ["A pairing that can grow together.", "You bring out the best stimulation in each other.", "The structure is favorable — you grow through each other."],
            "bodies": [
                "Not effortless, but structure has your back. The friction you feel is productive, not destructive.",
                "A relationship that doesn't fall apart easily. Your differences actually spark conversation.",
                "As long as you're willing to understand each other's differences, this deepens over time.",
            ],
        },
        "NEUTRAL": {
            "intros": ["The familiar and the new intersect.", "Now is the time to sync your rhythms.", "You intrigue each other with different charms."],
            "bodies": [
                "You respond differently to the same situations. That gap tires you sometimes and magnetizes you other times. Who smiles first in pivotal moments sets the temperature.",
                "It deepens when you honor each other's pace instead of forcing alignment. Trust you've built kicks in during hard moments.",
                "Acknowledging your differences lets this relationship grow in unexpected directions. Warm communication is the secret to lasting.",
            ],
        },
        "CAUTION": {
            "intros": ["A pairing that asks a lot.", "Now is a time of real friction.", "A relationship that especially needs honest talk."],
            "bodies": [
                "There's real friction. This isn't 'break up' — it's 'speak early, often, and honestly.'",
                "Avoiding each other's differences makes the problem bigger. Don't dodge uncomfortable talks.",
                "When emotions run hot, take half a beat. Building trust takes time.",
            ],
        },
        "CHALLENGING": {
            "intros": ["A pairing that asks everything.", "A structurally difficult relationship.", "Both of you must consciously put in effort."],
            "bodies": [
                "Structure pushes against both of you. The outcome isn't fixed, but most days require conscious will from both sides.",
                "Not an easy bond. But if the sincerity is real, you can cross this difficulty together.",
                "Your effort today shapes the relationship's future. Every small gesture makes a difference.",
            ],
        },
    },
    "ja": {
        "PEAK": {
            "intros": ["構造的に珍しいケミストリーです。", "四つの軸が珍しく整った組み合わせ。", "互いの形が自然にかみ合う稀な縁です。"],
            "bodies": [
                "何も保証はないけれど、この関係は多くの関係より多くを抱えられます。互いの可能性を一緒に開いていける珍しい土台があります。",
                "よくある組み合わせではありません。時間とともに互いを深く理解できる可能性が高いです。丁寧に扱えば長く続く縁です。",
                "構造が二人を支えています。今信頼を積み上げれば、どんな嵐にも揺れない関係になります。",
            ],
        },
        "FAVORABLE": {
            "intros": ["共に成長できる組み合わせです。", "互いに良い刺激を与える間柄です。", "構造が良好で、互いを通じて成長します。"],
            "bodies": [
                "自然に成る関係ではないけれど、構造が後ろで支えてくれます。感じる摩擦は破壊ではなく、生産的な種類です。",
                "簡単には崩れない関係です。違いがむしろ会話のきっかけになります。",
                "互いの違いを理解しようとする努力さえあれば、時間とともに深まります。",
            ],
        },
        "NEUTRAL": {
            "intros": ["慣れと新しさが交差しています。", "今は互いのリズムを合わせていく時期です。", "二人は異なる魅力で互いを刺激します。"],
            "bodies": [
                "同じ状況でも反応が異なる組み合わせです。その差は時に疲れを、時に魅力を生みます。決定的瞬間にどちらが先に笑うかが関係の温度を決めます。",
                "無理に合わせるより互いのペースを認める時、関係は深まります。積み重ねた信頼が難しい瞬間に力を発揮します。",
                "互いの違いを認める瞬間、関係は予想外の方向へ成長します。温かい対話が長続きの秘訣です。",
            ],
        },
        "CAUTION": {
            "intros": ["多くを求める組み合わせです。", "今は実質的な摩擦がある時期です。", "正直な対話が特に必要な関係です。"],
            "bodies": [
                "実質的な摩擦があります。別れろという意味ではなく、早く、頻繁に、正直に話してという意味です。",
                "互いの違いを避けると問題は大きくなります。不快な対話から逃げないでください。",
                "感情が先走る時ほど一拍置いて。信頼を築くには時間がかかります。",
            ],
        },
        "CHALLENGING": {
            "intros": ["すべてを求める組み合わせです。", "構造的に難しい関係です。", "二人とも意識的に努力すべき間柄です。"],
            "bodies": [
                "構造が二人に逆らいます。結果は決まっていませんが、ほとんどの日、二人とも意識的に意志を出す必要があります。",
                "簡単な関係ではありません。でも互いへの本心があれば、この難しさを一緒に越えられます。",
                "今の努力が関係の未来を決めます。小さな気遣いの一つひとつが大きな差を生みます。",
            ],
        },
    },
    "zh_cn": {
        "PEAK": {
            "intros": ["结构上罕见的化学反应。", "四个轴异常对齐的组合。", "彼此形态自然咬合的稀有缘分。"],
            "bodies": [
                "没什么能保证，但这段关系能承载的比大多数关系更多。你们有罕见的基础去共同展开彼此的潜力。",
                "不是常见的组合。随着时间推移，你们很可能更深地理解彼此。小心对待这段缘，它会持续很久。",
                "结构支撑着你们。现在积累信任，这会成为风雨不动的稳固关系。",
            ],
        },
        "FAVORABLE": {
            "intros": ["能够共同成长的组合。", "你们彼此成为良好刺激。", "结构友好，通过彼此成长。"],
            "bodies": [
                "不是自然而然的关系，但结构在身后支撑着。你们感受到的摩擦是生产性的，不是破坏性的。",
                "不会轻易崩塌的关系。你们的差异反而成为对话的契机。",
                "只要愿意理解彼此的差异，关系会随时间加深。",
            ],
        },
        "NEUTRAL": {
            "intros": ["熟悉与新鲜交错。", "现在是彼此调整节奏的时期。", "你们以不同的魅力彼此吸引。"],
            "bodies": [
                "面对相同情境反应各异的组合。这种差异有时令人疲惫，有时充满吸引力。关键时刻谁先微笑，决定关系的温度。",
                "与其勉强配合，不如尊重彼此的节奏，关系会加深。积累的信任在困难时刻发挥作用。",
                "承认差异的瞬间，关系会朝意想不到的方向成长。温暖的沟通是长久之道。",
            ],
        },
        "CAUTION": {
            "intros": ["要求很多的组合。", "现在是实质性摩擦的时期。", "特别需要坦诚对话的关系。"],
            "bodies": [
                "存在实质性摩擦。不是分手，而是提早、频繁、诚实地沟通。",
                "回避彼此的差异会让问题变大。不要逃避不舒服的对话。",
                "情绪先走时更要停顿一拍。积累信任需要时间。",
            ],
        },
        "CHALLENGING": {
            "intros": ["要求一切的组合。", "结构上困难的关系。", "两人都需要有意识地付出努力。"],
            "bodies": [
                "结构对你们不利。结果尚未确定，但大多数日子都需要双方有意识地拿出意志。",
                "不容易的关系。但若真心真实，你们能一起跨越这困难。",
                "今天的努力决定关系的未来。每一个小的体贴都带来大不同。",
            ],
        },
    },
    "es": {
        "PEAK": {
            "intros": ["Una química estructuralmente rara.", "Los cuatro ejes inusualmente alineados.", "Una conexión rara donde sus formas encajan naturalmente."],
            "bodies": [
                "Nada está garantizado, pero este vínculo puede sostener más que la mayoría. Tienen una base rara para desenvolver juntos su potencial.",
                "No es una combinación común. Hay una gran probabilidad de que se comprendan más profundamente con el tiempo. Cuiden este vínculo y perdurará.",
                "La estructura los respalda. Construyan confianza ahora y se volverá una relación que no se tambalea en ninguna tormenta.",
            ],
        },
        "FAVORABLE": {
            "intros": ["Una pareja que puede crecer junta.", "Se estimulan mutuamente de la mejor forma.", "La estructura es favorable — crecen a través del otro."],
            "bodies": [
                "No es sin esfuerzo, pero la estructura los respalda. La fricción que sienten es productiva, no destructiva.",
                "Una relación que no se desmorona fácilmente. Sus diferencias encienden la conversación.",
                "Mientras estén dispuestos a entender las diferencias del otro, esto se profundiza con el tiempo.",
            ],
        },
        "NEUTRAL": {
            "intros": ["Lo familiar y lo nuevo se cruzan.", "Es momento de sincronizar sus ritmos.", "Se intrigan mutuamente con encantos distintos."],
            "bodies": [
                "Responden diferente ante las mismas situaciones. Esa brecha a veces cansa, a veces atrae. Quién sonríe primero en los momentos clave marca la temperatura.",
                "Se profundiza cuando respetan el ritmo del otro en lugar de forzar alineación. La confianza construida actúa en los momentos difíciles.",
                "Reconocer las diferencias permite que esto crezca en direcciones inesperadas. La comunicación cálida es el secreto de la duración.",
            ],
        },
        "CAUTION": {
            "intros": ["Una pareja que pide mucho.", "Ahora es un tiempo de fricción real.", "Una relación que especialmente necesita hablar con honestidad."],
            "bodies": [
                "Hay fricción real. No es 'terminen' — es 'hablen pronto, seguido y con honestidad'.",
                "Evitar las diferencias hace más grande el problema. No escondan las conversaciones incómodas.",
                "Cuando las emociones se calientan, respiren. Construir confianza toma tiempo.",
            ],
        },
        "CHALLENGING": {
            "intros": ["Una pareja que pide todo.", "Una relación estructuralmente difícil.", "Ambos deben poner esfuerzo consciente."],
            "bodies": [
                "La estructura va contra ambos. El resultado no está fijado, pero la mayoría de días exigen voluntad consciente de ambos lados.",
                "No es un vínculo fácil. Pero si la sinceridad es real, pueden cruzar esta dificultad juntos.",
                "Su esfuerzo hoy moldea el futuro de la relación. Cada pequeño gesto hace la diferencia.",
            ],
        },
    },
}

def lang_key(p):
    raw = p.parent.name.lower()
    return "zh_cn" if raw.startswith("zh") else raw

# ========== 1. JSON 패치 ==========
print("=" * 55)
print("1) JSON: 등급별 intro/body 풀 추가")
print("=" * 55)
for f in Path("app/services/content/data").rglob("compatibility.json"):
    lang = lang_key(f)
    if lang not in TEMPLATES:
        continue
    with open(f, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    oc = data.get("OVERALL_CONTENT")
    if not isinstance(oc, dict):
        continue
    
    added = []
    for grade, tpl in TEMPLATES[lang].items():
        intros_key = f"{grade}_INTROS"
        bodies_key = f"{grade}_BODIES"
        if intros_key not in oc:
            oc[intros_key] = tpl["intros"]
            added.append(intros_key)
        if bodies_key not in oc:
            oc[bodies_key] = tpl["bodies"]
            added.append(bodies_key)
    
    if added:
        print(f"  ✅ {lang}: {added}")
        if APPLY:
            with open(f, "w", encoding="utf-8") as fp:
                json.dump(data, fp, ensure_ascii=False, indent=2)
    else:
        print(f"  ℹ️ {lang}: 이미 있음")

# ========== 2. writer.py 패치 ==========
print("\n" + "=" * 55)
print("2) writer.py: 템플릿 조합 로직")
print("=" * 55)

WRITER = Path("app/services/compatibility_writer.py")
if not WRITER.exists():
    print(f"❌ {WRITER} 없음")
    sys.exit(1)

txt = WRITER.read_text(encoding="utf-8")
orig = txt

# hashlib import 추가
if "import hashlib" not in txt:
    txt = "import hashlib\n" + txt
    print("  ✅ hashlib import 추가")

# 템플릿 선택 함수 삽입
if "_pick_template" not in txt:
    helper = '''

def _pick_template(overall_all: dict, grade: str, compat: dict, relationship_type: str) -> dict | None:
    """Deterministic hash로 intro + body 조합 선택."""
    intros = overall_all.get(f"{grade}_INTROS") or []
    bodies = overall_all.get(f"{grade}_BODIES") or []
    if not intros or not bodies:
        return None
    axes = compat.get("axes", {})
    parts = [grade, relationship_type]
    for k in ("elements", "day_master", "ten_gods", "sinsal"):
        ax = axes.get(k) or {}
        sc = ax.get("score")
        parts.append(f"{round(float(sc), 3)}" if isinstance(sc, (int, float)) else "0")
    seed = "|".join(parts)
    h = int(hashlib.md5(seed.encode()).hexdigest()[:12], 16)
    return {"headline": intros[h % len(intros)], "body": bodies[(h >> 16) % len(bodies)]}

'''
    # _write_axis 정의 앞에 삽입
    marker = "def _write_axis("
    if marker in txt:
        txt = txt.replace(marker, helper.strip() + "\n\n\n" + marker, 1)
        print("  ✅ _pick_template 함수 삽입")

# write_compatibility 내 NEUTRAL 블록 교체
old_block = '''    # NEUTRAL 등급이면 score 기반으로 variants 중 하나 선택 (반복 방지)
    if overall["grade"] == "NEUTRAL" and _overall_all.get("NEUTRAL_VARIANTS"):
        variants = _overall_all["NEUTRAL_VARIANTS"]
        try:
            s = (float(overall["score"]) + 1) / 2 * 100
        except (TypeError, ValueError):
            s = 50.0
        n = len(variants)
        idx = min(n - 1, max(0, int(round(s) * n // 100)))
        overall_content = variants[idx]
    else:
        overall_content = _overall_all.get(overall["grade"]) or _overall_all.get("NEUTRAL", {})'''

new_block = '''    # 템플릿 조합 우선, 없으면 기존 로직 fallback
    _tmpl = _pick_template(_overall_all, overall["grade"], compat, relationship_type)
    if _tmpl:
        overall_content = _tmpl
    elif overall["grade"] == "NEUTRAL" and _overall_all.get("NEUTRAL_VARIANTS"):
        variants = _overall_all["NEUTRAL_VARIANTS"]
        try:
            s = (float(overall["score"]) + 1) / 2 * 100
        except (TypeError, ValueError):
            s = 50.0
        n = len(variants)
        idx = min(n - 1, max(0, int(round(s) * n // 100)))
        overall_content = variants[idx]
    else:
        overall_content = _overall_all.get(overall["grade"]) or _overall_all.get("NEUTRAL", {})'''

if old_block in txt:
    txt = txt.replace(old_block, new_block, 1)
    print("  ✅ write_compatibility: 템플릿 조합 로직 삽입")
elif "_pick_template(" in txt and "_tmpl = " in txt:
    print("  ℹ️ 이미 패치됨")
else:
    print("  ❌ write_compatibility 패턴 불일치")
    sys.exit(1)

if txt != orig and APPLY:
    WRITER.write_text(txt, encoding="utf-8")

print()
if not APPLY:
    print("🧪 미리보기. 적용: python scripts/template_combination.py --apply")
else:
    print("🎉 패치 완료. 다음:")
    print("   .\\deploy.ps1")