# scripts/rewrite_poems_v2.py
"""
25개 시조 × 5개 언어 interpretation을 문맥 기반 완전 재작성.
sijo_ko, commentary, practice는 그대로 유지.
"""
import json
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
POEMS = Path("data/poems.json")

# ============================================================
# 25개 시조 × 5개 언어 = 125개 재작성 문장
# ============================================================
NEW = {
    # ══════════ 목(木) - 성장 ══════════
    "mok_same": {
        "ko": "이번 달은 당신의 성장과 같은 결입니다. 새순이 새순을 만나듯, 비슷한 힘이 서로를 밀어 올립니다.",
        "en": "This month shares the same grain as your growth. Like shoots meeting shoots, similar forces push each other upward.",
        "ja": "今月はあなたの成長と同じ木目です。新芽が新芽と出会うように、似た力が互いを押し上げます。",
        "zh_cn": "本月与你的成长同频。如同新芽遇见新芽，相似的力量彼此向上推动。",
        "es": "Este mes comparte el mismo grano que tu crecimiento. Como brotes que se encuentran, fuerzas similares se impulsan.",
    },
    "mok_generates_me": {
        "ko": "이번 달의 유연함이 당신의 성장을 조용히 밀어줍니다. 보이지 않는 곳에서 도움의 흐름이 도착합니다.",
        "en": "The month's flexibility quietly feeds your growth. Help arrives from unseen places.",
        "ja": "今月の柔軟性があなたの成長を静かに支えます。見えない場所から助けの流れが届きます。",
        "zh_cn": "本月的柔韧悄悄滋养你的成长。帮助从看不见的地方到来。",
        "es": "La flexibilidad del mes alimenta silenciosamente tu crecimiento. La ayuda llega desde lugares invisibles.",
    },
    "mok_i_generate": {
        "ko": "당신의 성장이 이번 달의 열정을 깨웁니다. 새순이 불꽃으로 피어나듯, 당신의 표현이 세상을 밝힙니다.",
        "en": "Your growth kindles the month's passion. Like shoots blooming into flame, your expression lights the world.",
        "ja": "あなたの成長が今月の情熱を灯します。新芽が炎に咲くように、あなたの表現が世界を照らします。",
        "zh_cn": "你的成长点燃本月的热情。如同新芽绽放成火焰，你的表达照亮世界。",
        "es": "Tu crecimiento enciende la pasión del mes. Como brotes que florecen en llama, tu expresión ilumina el mundo.",
    },
    "mok_i_control": {
        "ko": "당신의 성장이 이번 달의 안정을 붙잡아 중심을 세웁니다. 뿌리로 흙을 붙드는 나무처럼, 스스로 설 자리를 만드는 시기입니다.",
        "en": "Your growth steadies the month's stability. Like a tree gripping the earth with roots, you make a place to stand.",
        "ja": "あなたの成長が今月の安定をつかんで中心を定めます。根で大地をつかむ木のように、自ら立つ場所を作る時期です。",
        "zh_cn": "你的成长稳住本月的稳定，立起中心。如同根须抓住大地的树木，这是自筑根基的时期。",
        "es": "Tu crecimiento sostiene la estabilidad del mes. Como un árbol que agarra la tierra con raíces, haces tu propio lugar.",
    },
    "mok_controls_me": {
        "ko": "이번 달의 결단이 당신의 성장을 다듬습니다. 잘린 자리에서 새 가지가 돋듯, 지금의 정리가 다음 봄을 부릅니다.",
        "en": "The month's clarity prunes your growth. As new branches rise from the cut, today's clearing calls the next spring.",
        "ja": "今月の決断があなたの成長を整えます。切られた場所から新しい枝が伸びるように、今の整理が次の春を呼びます。",
        "zh_cn": "本月的决断修剪你的成长。如同切口处生新枝，今日的整理召唤下一个春天。",
        "es": "La claridad del mes poda tu crecimiento. Como nuevas ramas brotan del corte, la limpieza de hoy llama a la próxima primavera.",
    },
    # ══════════ 화(火) - 열정 ══════════
    "hwa_same": {
        "ko": "이번 달, 당신의 열정은 같은 방향의 열정과 만나 더 크게 타오릅니다. 밤이 빛을 삼킬 만큼 강렬하지만, 과열은 조심하세요.",
        "en": "This month, your passion meets a passion moving the same way and burns brighter. As intense as night swallowing the light — watch the heat.",
        "ja": "今月、あなたの情熱は同じ方向の情熱と出会い、より大きく燃え上がります。夜が光を飲み込むほど強い分、過熱には注意を。",
        "zh_cn": "本月，你的热情与同向的热情相遇，燃烧得更旺。夜吞噬光般强烈，请留意过热。",
        "es": "Este mes, tu pasión se encuentra con una pasión que va en la misma dirección y arde con más fuerza. Tan intensa como la noche que traga la luz — cuida el calor.",
    },
    "hwa_generates_me": {
        "ko": "이번 달의 성장이 당신의 열정에 장작을 댑니다. 나무가 불에게 길을 열어주듯, 받는 기운이 큰 시기입니다.",
        "en": "The month's growth feeds wood to your fire. As one gives way to the other, this is a season of receiving much.",
        "ja": "今月の成長があなたの情熱に薪をくべます。木が火に道を開くように、受け取る力が大きい時期です。",
        "zh_cn": "本月的成长为你的热情添柴。如同木为火开路，这是接收能量的时期。",
        "es": "El crecimiento del mes alimenta el fuego de tu pasión. Como uno cede al otro, esta es una temporada de recibir mucho.",
    },
    "hwa_i_generate": {
        "ko": "당신의 열정이 이번 달의 안정 위에 재를 남깁니다. 다 탄 자리에서 흙이 생기듯, 결과가 조용히 쌓이는 시기입니다.",
        "en": "Your passion leaves ash on the month's stability. As earth is born where fire finished, results quietly accumulate.",
        "ja": "あなたの情熱が今月の安定の上に灰を残します。燃え尽きた場所から土が生まれるように、結果が静かに積み重なります。",
        "zh_cn": "你的热情在本月的稳定之上留下灰。如同燃尽处生土，成果在悄然累积。",
        "es": "Tu pasión deja ceniza sobre la estabilidad del mes. Como la tierra nace donde el fuego terminó, los resultados se acumulan en silencio.",
    },
    "hwa_i_control": {
        "ko": "당신의 열정이 이번 달의 결단을 두드려 원하는 모양을 만듭니다. 쇠가 뜨거움을 기억하듯, 이 시도는 오래 남습니다.",
        "en": "Your passion hammers the month's clarity into shape. As metal remembers heat, this attempt will last.",
        "ja": "あなたの情熱が今月の決断を打って望む形にします。鉄が熱を覚えているように、この試みは長く残ります。",
        "zh_cn": "你的热情锤炼本月的决断，塑出理想之形。如同铁记住热，这次尝试将长久留存。",
        "es": "Tu pasión martilla la claridad del mes hasta darle forma. Como el metal recuerda el calor, este intento perdurará.",
    },
    "hwa_controls_me": {
        "ko": "이번 달의 유연함이 당신의 열정을 잠시 덮습니다. 꺼지는 대신, 김처럼 가볍게 하늘로 오르는 시기입니다.",
        "en": "The month's flexibility covers your fire. Rather than going out, you rise like steam toward the sky.",
        "ja": "今月の柔軟性があなたの情熱を一時的に覆います。消える代わりに、湯気のように軽く天へ昇る時期です。",
        "zh_cn": "本月的柔韧暂时覆盖你的热情。不是熄灭，而是如蒸汽般轻盈升空。",
        "es": "La flexibilidad del mes cubre tu fuego. En lugar de apagarte, asciendes como vapor hacia el cielo.",
    },
    # ══════════ 토(土) - 안정 ══════════
    "to_same": {
        "ko": "이번 달은 당신의 안정과 같은 결입니다. 흙이 흙을 만나 산이 되듯, 작은 것들이 조용히 쌓여 큰 중심이 됩니다.",
        "en": "This month shares your stability's grain. As earth meets earth to become a mountain, small things quietly build into a great center.",
        "ja": "今月はあなたの安定と同じ木目です。土が土と出会って山になるように、小さなものが静かに積み重なり大きな中心になります。",
        "zh_cn": "本月与你的稳定同频。如同土遇土成山，细小之物静静累积成大的中心。",
        "es": "Este mes comparte el grano de tu estabilidad. Como tierra con tierra se hace montaña, lo pequeño se acumula en un gran centro.",
    },
    "to_generates_me": {
        "ko": "이번 달의 열정이 당신의 안정을 따뜻하게 데웁니다. 다 탄 자리에서 흙이 일어나듯, 받쳐주는 힘이 강한 시기입니다.",
        "en": "The month's passion warms your stability. As earth rises where fire has finished, strong support holds you up.",
        "ja": "今月の情熱があなたの安定を温めます。燃え尽きた場所から土が立ち上がるように、支える力が強い時期です。",
        "zh_cn": "本月的热情温暖你的稳定。如同燃尽处土升起，这是支撑力量强劲的时期。",
        "es": "La pasión del mes calienta tu estabilidad. Como la tierra se eleva donde el fuego terminó, un fuerte apoyo te sostiene.",
    },
    "to_i_generate": {
        "ko": "당신의 안정이 이번 달의 결단을 길러냅니다. 흙이 쇠를 만들 듯, 단단한 결과가 조용히 나타나는 시기입니다.",
        "en": "Your stability grows the month's clarity. As earth forges metal, solid results quietly take shape.",
        "ja": "あなたの安定が今月の決断を育みます。土が鉄を作るように、固い結果が静かに現れる時期です。",
        "zh_cn": "你的稳定养育本月的决断。如同土炼出铁，坚实的成果悄然成形。",
        "es": "Tu estabilidad cultiva la claridad del mes. Como la tierra forja metal, los resultados sólidos toman forma en silencio.",
    },
    "to_i_control": {
        "ko": "당신의 안정이 이번 달의 유연함에 둑이 됩니다. 물이 논배미 안에서 제 길을 찾듯, 흐름을 정돈하는 시기입니다.",
        "en": "Your stability banks the month's flexibility. As water finds its way within the paddy, this is a season for channeling flow.",
        "ja": "あなたの安定が今月の柔軟性への堤防になります。水が田んぼの中で道を見つけるように、流れを整える時期です。",
        "zh_cn": "你的稳定成为本月柔韧的堤岸。如同水在田间找到自己的路，这是整理流向的时期。",
        "es": "Tu estabilidad encauza la flexibilidad del mes. Como el agua encuentra su camino en el arrozal, es temporada de ordenar el flujo.",
    },
    "to_controls_me": {
        "ko": "이번 달의 성장이 당신의 안정을 흔들어 새 길을 냅니다. 흙이 갈라진 자리에서 봄을 품듯, 다져지는 시기입니다.",
        "en": "The month's growth breaks through your stability. As earth holds spring within the crack, you are being pressed into firmness.",
        "ja": "今月の成長があなたの安定を揺らし、新しい道を開きます。割れた土が春を抱くように、固められる時期です。",
        "zh_cn": "本月的成长摇动你的稳定，开出新路。如同裂土怀抱春天，这是被压实的时期。",
        "es": "El crecimiento del mes rompe tu estabilidad. Como la tierra guarda la primavera en la grieta, te están prensando hacia la firmeza.",
    },
    # ══════════ 금(金) - 결단 ══════════
    "geum_same": {
        "ko": "이번 달은 당신의 결단과 같은 결입니다. 쇠가 쇠를 벼리듯, 서로 다른 각도에서 같은 방향을 향해 예리해집니다.",
        "en": "This month shares your clarity's grain. As steel sharpens steel, you grow sharper from another angle pointing the same way.",
        "ja": "今月はあなたの決断と同じ木目です。鉄が鉄を研ぐように、異なる角度から同じ方向へ鋭くなります。",
        "zh_cn": "本月与你的决断同频。如同钢磨钢，从不同角度朝同一方向变得锋利。",
        "es": "Este mes comparte el grano de tu claridad. Como el acero afila el acero, te agudizas desde otro ángulo hacia la misma dirección.",
    },
    "geum_generates_me": {
        "ko": "이번 달의 안정이 당신의 결단을 품어줍니다. 오랜 흙이 단단한 몸을 주듯, 안정된 기반 위에 서 있는 시기입니다.",
        "en": "The month's stability cradles your clarity. As long-laid earth gives a firm body, you stand on stable ground.",
        "ja": "今月の安定があなたの決断を抱きます。長年の土が固い体を与えるように、安定した土台の上に立つ時期です。",
        "zh_cn": "本月的稳定怀抱你的决断。如同经年之土给予坚实的形体，你站在稳固的根基之上。",
        "es": "La estabilidad del mes acuna tu claridad. Como la tierra longeva da cuerpo firme, pisas suelo estable.",
    },
    "geum_i_generate": {
        "ko": "당신의 결단이 이번 달의 유연함을 만들어냅니다. 서리 끝의 물이 강이 되듯, 흐름을 트는 시기입니다.",
        "en": "Your clarity gives rise to the month's flexibility. As frost-melt becomes a river, you open the way for flow.",
        "ja": "あなたの決断が今月の柔軟性を生み出します。霜の先の水が川になるように、流れを開く時期です。",
        "zh_cn": "你的决断造就本月的柔韧。如同霜融之水成河，这是开辟流向的时期。",
        "es": "Tu claridad da origen a la flexibilidad del mes. Como el deshielo se hace río, abres camino al flujo.",
    },
    "geum_i_control": {
        "ko": "당신의 결단이 이번 달의 성장을 정리합니다. 낫이 밭을 정돈하듯, 잘라내는 대신 다음 봄을 준비하는 시기입니다.",
        "en": "Your clarity clears the month's growth. As a sickle tidies the field, you cut away to prepare the next spring.",
        "ja": "あなたの決断が今月の成長を整えます。鎌が畑を整えるように、切り取って次の春を準備する時期です。",
        "zh_cn": "你的决断整理本月的成长。如同镰刀整理田地，割去是为下一个春天做准备。",
        "es": "Tu claridad despeja el crecimiento del mes. Como la hoz ordena el campo, cortas para preparar la próxima primavera.",
    },
    "geum_controls_me": {
        "ko": "이번 달의 열정이 당신의 결단을 두드려 단단하게 만듭니다. 불이 쇠를 단련하듯, 뜨거움 속에서 더 선명해지는 시기입니다.",
        "en": "The month's passion hammers your clarity into strength. As fire tempers steel, this heat makes you sharper.",
        "ja": "今月の情熱があなたの決断を打って強くします。火が鉄を鍛えるように、熱の中でより鮮明になる時期です。",
        "zh_cn": "本月的热情锤炼你的决断，使之更坚固。如同火炼钢，你在热度中变得更清晰。",
        "es": "La pasión del mes martilla tu claridad hacia la fuerza. Como el fuego templa el acero, este calor te hace más nítido.",
    },
    # ══════════ 수(水) - 유연 ══════════
    "su_same": {
        "ko": "이번 달은 당신의 유연함과 같은 결입니다. 물이 물을 만나 강이 되듯, 비슷한 힘들이 모여 깊어지는 시기입니다.",
        "en": "This month shares your flexibility's grain. As water meets water to become a river, similar forces gather into depth.",
        "ja": "今月はあなたの柔軟性と同じ木目です。水が水と出会って川になるように、似た力が集まって深くなる時期です。",
        "zh_cn": "本月与你的柔韧同频。如同水遇水成河，相似的力量汇聚而深邃。",
        "es": "Este mes comparte el grano de tu flexibilidad. Como agua con agua se hace río, fuerzas similares se reúnen en profundidad.",
    },
    "su_generates_me": {
        "ko": "이번 달의 결단이 당신의 유연함에 새로운 흐름을 열어줍니다. 서리 끝의 물이 몸으로 스미듯, 다시 흐르기 시작하는 시기입니다.",
        "en": "The month's clarity opens a new flow for your flexibility. As frost-melt seeps into the body, you begin to move again.",
        "ja": "今月の決断があなたの柔軟性に新しい流れを開きます。霜の先の水が体に染み込むように、再び流れ始める時期です。",
        "zh_cn": "本月的决断为你的柔韧开新流。如同霜水渗入身体，你再次开始流动。",
        "es": "La claridad del mes abre un nuevo flujo para tu flexibilidad. Como el deshielo se filtra en el cuerpo, vuelves a moverte.",
    },
    "su_i_generate": {
        "ko": "당신의 유연함이 이번 달의 성장을 깨웁니다. 땅속의 물이 뿌리를 두드리듯, 새순을 키우는 시기입니다.",
        "en": "Your flexibility wakes the month's growth. As underground water taps the roots, this is a season for bringing shoots to life.",
        "ja": "あなたの柔軟性が今月の成長を目覚めさせます。地下の水が根を叩くように、新芽を育てる時期です。",
        "zh_cn": "你的柔韧唤醒本月的成长。如同地下水叩击根须，这是培育新芽的时期。",
        "es": "Tu flexibilidad despierta el crecimiento del mes. Como el agua subterránea golpea las raíces, es temporada de dar vida a los brotes.",
    },
    "su_i_control": {
        "ko": "당신의 유연함이 이번 달의 열정을 잠시 덮습니다. 물이 불을 덮어도 불이 김으로 오르듯, 열기를 식히면서 더 멀리 가는 시기입니다.",
        "en": "Your flexibility covers the month's passion. As water covers fire yet fire rises as steam, cooling down lets you go farther.",
        "ja": "あなたの柔軟性が今月の情熱を一時的に覆います。水が火を覆っても火が湯気で昇るように、熱を冷まして遠くへ進む時期です。",
        "zh_cn": "你的柔韧暂时覆盖本月的热情。如同水覆火而火以蒸汽升腾，冷却反而能走得更远。",
        "es": "Tu flexibilidad cubre la pasión del mes. Como el agua cubre el fuego pero este asciende como vapor, enfriarte te lleva más lejos.",
    },
    "su_controls_me": {
        "ko": "이번 달의 안정이 당신의 유연함에 둑을 만들어줍니다. 흙이 물길을 감싸 안듯, 경계 안에서 더 깊어지는 시기입니다.",
        "en": "The month's stability builds a bank around your flexibility. As earth cradles the river, you deepen within the bounds.",
        "ja": "今月の安定があなたの柔軟性に堤防を作ります。土が水の道を抱くように、境界の中でより深くなる時期です。",
        "zh_cn": "本月的稳定为你的柔韧筑起堤岸。如同土怀抱河道，你在边界中愈加深邃。",
        "es": "La estabilidad del mes tiende un cauce a tu flexibilidad. Como la tierra abraza al río, te profundizas dentro de los límites.",
    },
}

# ============================================================
# 패치 실행
# ============================================================
print("=" * 55)
print("data/poems.json interpretation 재작성")
print("=" * 55)

if not POEMS.exists():
    print(f"❌ {POEMS} 없음")
    sys.exit(1)

with open(POEMS, "r", encoding="utf-8") as f:
    data = json.load(f)

poems = data.get("poems", [])
print(f"📖 총 {len(poems)}개 시조\n")

changed = 0
missing = []
for p in poems:
    pid = p.get("id", "")
    if pid not in NEW:
        missing.append(pid)
        continue
    tr = p.get("translations", {})
    for lang, new_text in NEW[pid].items():
        if lang not in tr:
            tr[lang] = {}
        old = tr[lang].get("interpretation", "")
        if old != new_text:
            tr[lang]["interpretation"] = new_text
            changed += 1

print(f"🔄 재작성: {changed}문장")
if missing:
    print(f"⚠️ NEW에 없는 시조 ID: {missing}")

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/rewrite_poems_v2.py --apply")
    sys.exit(0)

with open(POEMS, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n🎉 저장 완료: {POEMS}")
print("   다음: .\\deploy.ps1")