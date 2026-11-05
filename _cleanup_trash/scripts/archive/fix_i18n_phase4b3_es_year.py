#!/usr/bin/env python3
"""
Phase 4-B3: es/year.json YEAR_THEME_CONTENT 번역 (배치 3/5).
- TEN_GOD_INDIRECT_WEALTH (3 variants)
- TEN_GOD_DIRECT_WEALTH (3 variants)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ES_YEAR = ROOT / "app" / "services" / "content" / "data" / "es" / "year.json"

TRANSLATIONS = {
    "TEN_GOD_INDIRECT_WEALTH": [
        {
            "name": "El Marinero que Surca la Ola de la Oportunidad",
            "headline": "Este año, renacerás como un planificador dinámico que captura un valor masivo en medio de las olas del feroz cambio.",
            "body": (
                "A lo largo de este año, renacerás como alguien que captura flexiblemente las oportunidades de un mundo en constante movimiento en lugar de quedarte en una forma fija. Expandirás audazmente tu territorio reconociendo posibilidades infravaloradas que otros no pueden ver a simple vista.\n\n"
                "Leerás intuitivamente los cambios en el mercado y las tendencias e intentarás apuestas audaces en el lugar correcto. El entorno siempre cambiante se convierte en sí mismo en un emocionante patio de juegos y un enorme mar de oportunidades para ti.\n\n"
                "La agilidad empresarial y la escalabilidad demostradas a lo largo del año elevan tu estilo de vida a un nivel superior. Las ganancias y los logros generados por rutas inesperadas añaden vitalidad a tu vida.\n\n"
                "La capacidad de mantener varias posibilidades abiertas y responder con flexibilidad se convierte en tu mejor arma este año. Disfruta de una aventura emocionante como un marinero que disfruta de las olas del cambio."
            ),
            "watch_for": "Asumir demasiadas cosas a la vez y resultar en una finalización deficiente.",
            "lean_into": "Expandir tu territorio abriendo tu mente a diversas posibilidades y asumiendo riesgos calculados.",
        },
        {
            "name": "El Pionero que Cruza Fronteras",
            "headline": "Este año, te convertirás en un desafiante que va más allá de los dominios existentes y abre nuevos caminos.",
            "body": (
                "Este año es un tiempo de crecimiento tridimensional, rompiendo cercas familiares y abriendo nuevos mercados y oportunidades frescas. Obtendrás resultados inesperados al adaptarte ágilmente a los cambios en las situaciones y combinar ingeniosamente recursos inactivos.\n\n"
                "Encuentras nuevos puntos de sinergia cruzando este y aquel campo sin estar atado a un solo método. Tu mentalidad flexible abre un poderoso avance en una vida diaria estancada.\n\n"
                "Los caminos diversificados pavimentados a lo largo del año se convertirán en activos sólidos para hacer fértil tu futuro. La emocionante sensación de logro de nuevos desafíos llena tu vida diaria de una gran emoción.\n\n"
                "Adopta la audacia de deshacerte del pensamiento estereotipado y avanzar hacia una tierra vasta. Tu espíritu desafiante este año escribirá una nueva fórmula de éxito que el mundo notará."
            ),
            "watch_for": "Una actitud ligera que busca solo tentaciones especulativas no verificadas o suerte.",
            "lean_into": "Intentar flexiblemente colaboraciones entre diferentes industrias o nuevos modelos de negocio.",
        },
        {
            "name": "El Mago de la Reasignación de Recursos",
            "headline": "A lo largo de este año, te convertirás en un estratega que maximiza los recursos ocultos con una perspectiva tridimensional.",
            "body": (
                "Este año se desarrolla una narrativa de reconectar activos estancados e información con un ojo creativo y sublimarlos en un valor masivo. Demostrarás un excelente sentido para convertir cualquier situación inesperada en una oportunidad inmediata.\n\n"
                "Demuestras una destacada capacidad para reunir redes dispersas, información y recursos materiales para crear un tablero valioso. Incluso las cosas que parecen triviales se transforman en un enorme valor añadido a través de tus manos.\n\n"
                "Completar el espectro masivo que soñaste llega cuando exploras el mundo con una mente abierta a lo largo del año. Tus habilidades de afrontamiento flexibles y ágiles atraen la envidia y la admiración de quienes te rodean.\n\n"
                "Amplía tu perspectiva sobre el manejo de recursos e intenta combinaciones audaces. La táctica que demuestres este año te traerá tanto recompensas prácticas como honor."
            ),
            "watch_for": "Dejarte cegar por las ganancias a corto plazo y descuidar la sustancia y lo básico a largo plazo.",
            "lean_into": "Diversificar nuevos canales de creación de valor con una actitud flexible y abierta.",
        },
    ],
    "TEN_GOD_DIRECT_WEALTH": [
        {
            "name": "El Arquitecto de un Castillo Sólido",
            "headline": "Este año, te convertirás en alguien que acumula activos sólidos insustituibles a través de una disciplina silenciosa y la fidelidad.",
            "body": (
                "La narrativa que recorre este año es la fidelidad de excluir la suerte y apilar constantemente torres prácticas día a día. Brillan los sentidos realistas y las habilidades de gestión precisas, estableciendo una base estable e inquebrantable.\n\n"
                "Brilla tu actitud de mantener firmemente los principios y rutinas establecidos sin dejarte sacudir por tentaciones inmediatas. La meticulosidad que no permite un solo margen de error protege firmemente tus finanzas y tu carrera.\n\n"
                "El sistema cuidadosamente establecido a lo largo de un año te presentará un profundo sentido de estabilidad que no colapsará en toda la vida. Los logros acumulados prácticamente ponen una fuerza sólida sobre tus hombros.\n\n"
                "Se desarrolla un tiempo glorioso que demuestra que la consistencia es el camino más rápido. La base realista que construyes este año se convierte en una fortaleza robusta que apoya todos los desafíos futuros."
            ),
            "watch_for": "Bloquear las oportunidades de un cambio fresco debido a actitudes excesivamente conservadoras.",
            "lean_into": "Estandarizar las rutinas centrales y los sistemas de gestión de activos para promover el crecimiento compuesto.",
        },
        {
            "name": "El Guardián del Valor Honesto",
            "headline": "Este año, te convertirás en una figura que cumple perfectamente sus deberes y recibe un profundo respeto y confianza.",
            "body": (
                "Este año es un tiempo en el que el noble poder de la honestidad y la consistencia se demuestra más claramente en tu vida. Establecerás una posición sólida en la organización y la sociedad gestionando perfectamente las promesas y tareas diarias que parecen triviales.\n\n"
                "Tu actitud de demostrar confianza a través de acciones en lugar de palabras inspira profundamente a quienes te rodean. Tu apariencia de completar tareas en silencio sin evadir la responsabilidad en ningún lugar conduce a la mejor reputación.\n\n"
                "La reputación acumulada a lo largo del año regresa como un activo masivo que no se puede cambiar por nada. Las personas creen en tu gravedad y fidelidad y te confían voluntariamente tareas importantes.\n\n"
                "Será un año gratificante que confirma la verdad de que el sudor honesto no traiciona. Una brillante corona de confianza se coloca en cada paso que das caminando derecho mientras mantienes los principios."
            ),
            "watch_for": "Obsesionarte excesivamente con pequeños indicadores o detalles y cansarte.",
            "lean_into": "Organizar con precisión la sustancia de la vida y acumular los frutos del logro honesto.",
        },
        {
            "name": "El Maestro del Interés Compuesto",
            "headline": "A lo largo de este año, lograrás un crecimiento silencioso pero abrumador dentro de un sistema organizado.",
            "body": (
                "Este año es un año para corregir el desorden de la vida diaria y acumular gradualmente logros masivos sobre bases sólidas. Crearás una sustancia sólida al sumergirte profundamente en las cosas que puedes controlar sin estar atado a la incertidumbre.\n\n"
                "Experimentarás la magia del interés compuesto que se hincha como una bola de nieve con el tiempo al gestionar sistemáticamente pequeños hábitos y activos. El crecimiento poco llamativo pero sustancial crea una sinergia explosiva.\n\n"
                "Donde te encuentres después de un año será incomparablemente más sólido y tranquilo que antes. El sistema diario inquebrantable te trae una enorme riqueza y estabilidad.\n\n"
                "Demuestra la sabiduría de concentrarte en pequeños avances diarios, desechando la impaciencia. La torre del éxito que durará toda la vida se completa sobre la base sólida que pusiste este año."
            ),
            "watch_for": "Una actitud de evaluar todo tu valor únicamente por resultados inmediatos o números.",
            "lean_into": "Construir hábitos saludables y bases prácticas que sean sostenibles a largo plazo.",
        },
    ],
}


def main() -> int:
    if not ES_YEAR.exists():
        print(f"❌ {ES_YEAR} 없음")
        return 1

    data = json.loads(ES_YEAR.read_text(encoding="utf-8"))
    if "YEAR_THEME_CONTENT" not in data:
        print("❌ YEAR_THEME_CONTENT 없음")
        return 1

    for key, variants in TRANSLATIONS.items():
        if len(variants) != 3:
            print(f"❌ {key}: variant 수 {len(variants)} (3이어야 함)")
            return 1
        data["YEAR_THEME_CONTENT"][key] = variants
        print(f"✅ {key}: {len(variants)} variants")

    ES_YEAR.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\n✅ {ES_YEAR.name} 저장 완료")

    # 검증
    print("\n[verify]")
    data2 = json.loads(ES_YEAR.read_text(encoding="utf-8"))
    ytc = data2["YEAR_THEME_CONTENT"]
    checks = [
        ("TEN_GOD_INDIRECT_WEALTH", 0, "name", "El Marinero que Surca la Ola de la Oportunidad"),
        ("TEN_GOD_INDIRECT_WEALTH", 2, "lean_into", "Diversificar nuevos canales de creación de valor con una actitud flexible y abierta."),
        ("TEN_GOD_DIRECT_WEALTH", 0, "name", "El Arquitecto de un Castillo Sólido"),
        ("TEN_GOD_DIRECT_WEALTH", 2, "headline", "A lo largo de este año, lograrás un crecimiento silencioso pero abrumador dentro de un sistema organizado."),
    ]
    ok = True
    for god, idx, field, expected in checks:
        actual = ytc[god][idx][field]
        if actual == expected:
            print(f"  [OK] {god}[{idx}].{field}")
        else:
            print(f"  [ERR] {god}[{idx}].{field}: got {actual!r}")
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())