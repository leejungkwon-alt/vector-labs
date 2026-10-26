#!/usr/bin/env python3
"""
Phase 4-B2: es/year.json YEAR_THEME_CONTENT 번역 (배치 2/5).
- TEN_GOD_EATING_GOD (3 variants)
- TEN_GOD_HURTING_OFFICER (3 variants)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ES_YEAR = ROOT / "app" / "services" / "content" / "data" / "es" / "year.json"

TRANSLATIONS = {
    "TEN_GOD_EATING_GOD": [
        {
            "name": "La Fuente de la Abundante Creación",
            "headline": "Este año, te convertirás en un artesano que crea libremente según tu propia naturaleza y enriquece tu vida cotidiana.",
            "body": (
                "A lo largo de este año, tu vida se llenará de una alegría creativa que fluye naturalmente, no de una lucha forzada. Basándote en tus sentidos y capacidad expresiva innatos, te revelarás con honestidad y te comunicarás cálidamente con el mundo.\n\n"
                "Te sumergirás profundamente en el placer de moldear ideas que brotan de lo profundo en resultados concretos en tu vida diaria. La verdadera habilidad se demuestra solo cuando te concentras por completo en tu propio gusto y naturaleza en lugar de adaptarte a los estándares de los demás.\n\n"
                "Tu marca única y tus planes cuidadosamente cultivados a lo largo de un año traerán frutos abundantes con el tiempo. Las creaciones que produzcas presentarán una inspiración fresca a quienes te rodean.\n\n"
                "Una actitud de cultivar tu vida diaria como arte con una mente relajada trae una gran fortuna. Este año, deja una hermosa huella en el mundo a tu propio ritmo y compás."
            ),
            "watch_for": "Volverte demasiado complaciente en la comodidad y perder la disciplina mínima y los horarios.",
            "lean_into": "Concretar tus ideas y valores únicos en proyectos a largo plazo.",
        },
        {
            "name": "El Artista que Disfruta la Vida",
            "headline": "Este año, te convertirás en alguien que descubre el verdadero valor de la abundancia en las pequeñas alegrías de la vida cotidiana.",
            "body": (
                "Este año es un viaje para romper con las evaluaciones de los demás o la presión orientada al rendimiento y pulir tu propia vida como una obra de arte. Ganarás una gran paz interior al sumergirte puramente en lo que amas y cuidar cuidadosamente tu cuerpo y mente.\n\n"
                "Incluso en la ajetreada vida diaria, no te perderás las pequeñas alegrías, y recargarás tu energía a través de comida deliciosa, buena música y conversaciones cálidas. Esta riqueza emocional crea un milagro que más bien aumenta la eficiencia del trabajo.\n\n"
                "Vivir con un corazón sincero a lo largo del año revela resultados naturales y de maduración lenta tanto en el trabajo como en la vida. No necesitas apresurarte; las cálidas semillas que plantaste florecerán bellamente por sí solas.\n\n"
                "Te darás cuenta de cuán poderoso es una actitud de disfrutarte y consolarte en lugar de fustigarte. Este año, tu vida diaria misma se convierte en el refugio más cómodo y maravilloso."
            ),
            "watch_for": "Una actitud de posponer metas a largo plazo dejándote llevar por el placer y la comodidad a corto plazo.",
            "lean_into": "Construir un estilo de vida donde el descanso sostenible y la creación pura estén en armonía.",
        },
        {
            "name": "El Cultivador de Cálidos Valores",
            "headline": "A lo largo de este año, te convertirás en el sujeto que ilumina brillantemente los corazones de quienes te rodean con calidez y buena voluntad.",
            "body": (
                "Este año es un año hermoso donde tu cálida sensibilidad y tu generoso compartir cambian suavemente el mundo que te rodea. Consolidarás una presencia insustituible al compartir la alegría que sientes y el conocimiento útil con las personas.\n\n"
                "Las personas a tu alrededor obtendrán una gran fuerza del cálido consuelo y las nuevas ideas que ofreces. Experimentarás un círculo virtuoso donde la buena voluntad que otorgas circula y regresa a ti como una suerte aún mayor.\n\n"
                "La autenticidad acumulada constantemente como si araras un campo a lo largo de un año se convierte en la magia que enriquece toda tu vida. Continúa un tiempo precioso donde sientes una verdadera recompensa y felicidad en las sonrisas de las personas.\n\n"
                "Experimentarás plenamente la esencia del valor que crece cuanto más compartes. Este año se registra como un año en el que tu buena influencia insufla un claro calor al mundo."
            ),
            "watch_for": "Descuidar las promesas mínimas y los sistemas bajo el pretexto de la libertad.",
            "lean_into": "Dejar tu perspectiva y expresión únicas como contenido o trabajos continuos de formato largo.",
        },
    ],
    "TEN_GOD_HURTING_OFFICER": [
        {
            "name": "El Icono de la Innovación y la Reforma",
            "headline": "Este año, crecerás hasta convertirte en un innovador que rompe los estereotipos de la época y propone un nuevo paradigma.",
            "body": (
                "Este año es un año para romper audazmente los frustrantes marcos antiguos y las costumbres irrazonables del pasado y presentar tu visión única al mundo. Renacerás como un orgulloso protagonista que capta con precisión las ineficiencias que otros pasan por alto y presenta alternativas innovadoras.\n\n"
                "Lanzarás agudos conocimientos a organizaciones estancadas o sistemas antiguos y liderarás los vientos del cambio. Tu agudo análisis y tu implacable ejecución dejarán una profunda impresión en quienes te rodean.\n\n"
                "La ardiente pasión y el poder de persuasión que demostrarás a lo largo del año cambiarán por completo el panorama de la organización y el mercado. La sensación de un pionero que no teme al cambio llena emocionantemente todo tu cuerpo.\n\n"
                "Se crean logros masivos cuando viertes tu sentido de justicia y tu voluntad de reforma en una dirección constructiva. Este año es un tiempo glorioso en el que tu voz se convierte en una energía poderosa que cambia el mundo."
            ),
            "watch_for": "Hacerte enemigo de tus aliados con comentarios excesivamente agudos y contundentes.",
            "lean_into": "Liderar proyectos innovadores que mejoren estructuras antiguas ineficientes.",
        },
        {
            "name": "El Portavoz Inspirador",
            "headline": "Este año, te convertirás en una estrella que cautiva el corazón del público con una voz segura y una marca personal.",
            "body": (
                "Este año es un tiempo dinámico en el que tus brillantes sentidos estéticos y tu genial poder expresivo reciben la atención del mundo. Marcarás efectivamente tus creencias y mensajes internos para presentar una inspiración intensa a las personas.\n\n"
                "Cuando expreses tus pensamientos al mundo sin dudar, innumerables personas se enamorarán de tu encanto. Tu sentido para leer las tendencias se vuelve excepcionalmente agudo, maximizando tu poder para fascinar al público.\n\n"
                "A lo largo del año, alzar tu voz con confianza hacia el mundo te permitirá experimentar el hecho de ocupar el centro del escenario. Disfruta de la alegría de que tu nombre se convierta en una marca poderosa.\n\n"
                "No hay mejor momento que ahora para imprimir tu estilo único en el mundo. Florece tus talentos plenamente bajo el brillante foco."
            ),
            "watch_for": "Derrochar energía en críticas o rebeldía sin fundamento simplemente para oponerte a las reglas.",
            "lean_into": "Perseguir una campaña de marca a gran escala para publicitar ampliamente tu mensaje.",
        },
        {
            "name": "El Arquitecto que Traza un Nuevo Tablero",
            "headline": "A lo largo de este año, te convertirás en alguien que se sacude las costumbres estancadas y crea un nuevo camino adaptado a los tiempos.",
            "body": (
                "Este año se desarrolla una narrativa a largo plazo en la que reformas constructivamente los sistemas antiguos y guías a las personas bajo un estandarte pionero. Recrearás entornos atrapados en el pantano de la convención con agudos conocimientos y establecerás nuevos estándares que generen admiración.\n\n"
                "Buscas mejores alternativas cuestionando la obediencia incondicional o las prácticas irrazonables. Tu plan de reforma racional sacia la larga sed de quienes te rodean y les insufla nueva vitalidad.\n\n"
                "Tu reforma, añadida con consideración y sabiduría, abrirá un nuevo camino de esperanza para muchos. Demuestras las cualidades de un verdadero líder en el proceso de sacudir viejos legados y diseñar un marco orientado al futuro.\n\n"
                "Maximiza los resultados de la reforma persuadiendo a los demás con una comunicación sabia y suave. El nuevo tablero que diseñes este año ejercerá una influencia masiva en los años venideros."
            ),
            "watch_for": "Mostrar una ira impaciente hacia las personas lentas o conservadoras.",
            "lean_into": "Rediseñar procedimientos anacrónicos en sistemas modernos y flexibles.",
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
        ("TEN_GOD_EATING_GOD", 0, "name", "La Fuente de la Abundante Creación"),
        ("TEN_GOD_EATING_GOD", 2, "lean_into", "Dejar tu perspectiva y expresión únicas como contenido o trabajos continuos de formato largo."),
        ("TEN_GOD_HURTING_OFFICER", 0, "name", "El Icono de la Innovación y la Reforma"),
        ("TEN_GOD_HURTING_OFFICER", 1, "watch_for", "Derrochar energía en críticas o rebeldía sin fundamento simplemente para oponerte a las reglas."),
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