#!/usr/bin/env python3
"""
Phase 4-B4: es/year.json YEAR_THEME_CONTENT 번역 (배치 4/5).
- TEN_GOD_SEVEN_KILLINGS (3 variants)
- TEN_GOD_DIRECT_OFFICER (3 variants)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ES_YEAR = ROOT / "app" / "services" / "content" / "data" / "es" / "year.json"

TRANSLATIONS = {
    "TEN_GOD_SEVEN_KILLINGS": [
        {
            "name": "El Protagonista de un Salto Heroico",
            "headline": "Este año, te convertirás en un líder que atraviesa duras pruebas de frente y logra una reversión masiva.",
            "body": (
                "La narrativa a largo plazo que recorre este año es el viaje de un héroe que cruza una montaña masiva con coraje y determinación y finalmente logra la victoria. Revelas tu espíritu fuerte y oculto al aceptar directamente desafíos de alta dificultad y responsabilidades pesadas que querías evitar.\n\n"
                "Brillas aún más en la primera línea donde otros quieren huir, convirtiendo la presión feroz en oportunidades. Tu determinación audaz y tu impulso se convierten en un salvador que rescata a la organización en tiempos de crisis.\n\n"
                "Habiendo completado el entrenamiento del año, serás un héroe sólido que mantiene la calma en cualquier crisis. Te enfrentarás a un yo más maduro, llevando las duras pruebas como medallas.\n\n"
                "Abre camino a través de las tareas de este año de frente con el corazón de un león que lucha contra el miedo. El sudor que derramaste se completará como la narrativa de éxito más dramática."
            ),
            "watch_for": "Trabajar en exceso tu mente y tu cuerpo o presionar a los demás obsesionándote demasiado con lograr metas.",
            "lean_into": "Abrir camino a través de tareas de alta dificultad de frente basándote en una responsabilidad audaz.",
        },
        {
            "name": "Entrenamiento a Través del Crisol",
            "headline": "Este año, renacerás como un maestro interior usando la presión severa como el mejor nutriente.",
            "body": (
                "Este año es un año de audacia para quemar tus debilidades y miedos y completar un carácter duro como el hierro. Logras un nivel diferente de rendimiento demostrando una asombrosa concentración en situaciones que exigen una alta responsabilidad.\n\n"
                "La presión y el estrés que se aprietan desde todos lados se convierten más bien en un crisol que lleva tu potencial al extremo. Destrozas fríamente los muros masivos que no te atrevías a imaginar antes.\n\n"
                "La sólida confianza establecida a lo largo de un año te protegerá firmemente contra cualquier tormenta. Como el acero que ha pasado por un duro templado, tu ser interior posee una firmeza que nadie puede romper.\n\n"
                "Experimenta las pruebas de frente sin evitarlas y absorbe la fuerza interior. El dolor feroz de este año se convierte en un fundamento sagrado para la gloria más brillante de mañana."
            ),
            "watch_for": "Tomar actitudes excesivamente defensivas o agresivas hacia los estímulos externos.",
            "lean_into": "Revertir los desafíos más difíciles en los mejores peldaños para tu crecimiento.",
        },
        {
            "name": "La Decisión que Cambia el Tablero",
            "headline": "A lo largo de este año, resolverás por completo las tareas pendientes de mucho tiempo que estaban enredadas con una excelente determinación.",
            "body": (
                "Este año es un año para cortar los problemas estancados durante mucho tiempo con una sola decisión y abrir un nuevo horizonte. Muestras la audacia de concentrar toda tu energía en los valores esenciales sin dejarte influir por los sentimientos personales.\n\n"
                "Das la vuelta al tablero por completo a través de una audaz reestructuración y decisiones, como cortar un nudo complejo y enredado con un solo cuchillo. Tu carisma, que calma las preocupaciones a tu alrededor en un solo golpe, alcanza su punto máximo.\n\n"
                "El liderazgo digno y audaz que demostrarás a lo largo del año dejará una profunda huella en quienes te rodean. Los resultados impulsados con determinación hacen que tu posición sea sólida como una fortaleza natural.\n\n"
                "Blande la hoja afilada que corta los apegos persistentes y apunta al núcleo. La audaz decisión que tomes este año cambia por completo el flujo de tu vida hacia la victoria."
            ),
            "watch_for": "Continuar exigiéndote como en una emergencia sin suficiente descanso y agotarte.",
            "lean_into": "Organizar audazmente las tareas innecesarias y concentrarte en las tareas más esenciales.",
        },
    ],
    "TEN_GOD_DIRECT_OFFICER": [
        {
            "name": "El Guardián de los Principios Nobles",
            "headline": "Este año, te convertirás en alguien que asciende a un rango honorable con procedimientos correctos y un carácter elevado.",
            "body": (
                "A lo largo de este año, establecerás una autoridad oficial y confianza basadas en un carácter recto y principios correctos. Recibirás el respeto voluntario y el apoyo de muchas personas manteniendo una comunicación transparente y actitudes justas.\n\n"
                "Tu apariencia de mantener rectamente los principios sin buscar suerte ni usar métodos expeditivos da una gran resonancia a quienes te rodean. Tu actitud recta se convierte en sí misma en una brújula que endereza la disciplina de la organización y eleva su dignidad.\n\n"
                "La reputación y el honor establecidos dignamente a lo largo de un año se convertirán en una corona sólida para tu carrera. Disfrutas de la alegría de ascender rápidamente en el estatus social al asumir títulos oficiales o posiciones.\n\n"
                "Avanza hacia el honor noble con una alta moralidad y responsabilidad como armas. Los pasos basados en principios que das este año se convierten en un legado brillante que sirve de ejemplo a otros durante mucho tiempo."
            ),
            "watch_for": "Estar excesivamente atado a las miradas de los demás o a las evaluaciones sociales y perder la libertad.",
            "lean_into": "Establecer una posición oficial y autoridad manteniendo altos estándares éticos y procedimientos.",
        },
        {
            "name": "La Piedra Angular de la Confianza",
            "headline": "Este año, te establecerás como un pilar sólido indispensable en la comunidad a la que perteneces.",
            "body": (
                "Este año es un tiempo para establecer un orden organizado y estándares claros, dando un gran alivio a la organización y la familia. Demuestras una presencia insustituible en el proceso de cumplir estrictamente las promesas y cumplir impecablemente tus deberes.\n\n"
                "El lugar donde estás se convierte en sí mismo en una zona segura, y quienes te rodean se apoyan en tu solidez y disfrutan de la paz. Tu actitud ordenada y ejemplar sostiene de manera saludable a toda la comunidad.\n\n"
                "La profunda estabilidad arraigada a lo largo del año te convierte en el maestro y apoyo en el que quienes te rodean más confían. Te haces cargo del eje central de la comunidad como una figura clave que nadie puede negar.\n\n"
                "Crea un orden sostenible construyendo un proceso sistemático y transparente. Un edificio de éxito más sólido y brillante se eleva sobre la piedra angular que pusiste este año."
            ),
            "watch_for": "Sufrir un estrés excesivo atrapado en el marco de obligaciones y disciplina autoimpuestas.",
            "lean_into": "Construir pautas transparentes y sistemáticas para crear un orden sostenible.",
        },
        {
            "name": "El Arquitecto del Orden Armonioso",
            "headline": "A lo largo de este año, liderarás una paz y un éxito sólidos armonizando principios y consideración.",
            "body": (
                "Este año es un año para organizar meticulosamente roles y sistemas ambiguos y completar un entorno óptimo donde todos puedan coexistir. Tu dignidad de tomar procedimientos legítimos sin buscar suerte da frutos como el mejor logro.\n\n"
                "Logras una armonía perfecta agregando un abrazo cálido y un sentido de equilibrio en lugar de solo mantener un estándar estricto. Construyes un sistema ideal donde las reglas y la humanidad se mezclan bellamente.\n\n"
                "Después de un año, tu vida disfrutará de una profunda paz dentro de un orden ordenado y elegante. El entorno caótico que te rodea recupera perfectamente la estabilidad gracias a tu toque ordenado.\n\n"
                "Demuestra un liderazgo sabio que mantiene los principios pero abraza a las personas. El orden armonioso que completas este año se convierte en el castillo de éxito más elegante que no colapsará en toda la vida."
            ),
            "watch_for": "Una mente que retrasa la toma de decisiones o se impacienta debido a un perfeccionismo excesivo.",
            "lean_into": "Sentar las bases para recibir un reconocimiento claro, como contratos oficiales o certificaciones.",
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
        ("TEN_GOD_SEVEN_KILLINGS", 0, "name", "El Protagonista de un Salto Heroico"),
        ("TEN_GOD_SEVEN_KILLINGS", 2, "lean_into", "Organizar audazmente las tareas innecesarias y concentrarte en las tareas más esenciales."),
        ("TEN_GOD_DIRECT_OFFICER", 0, "name", "El Guardián de los Principios Nobles"),
        ("TEN_GOD_DIRECT_OFFICER", 2, "watch_for", "Una mente que retrasa la toma de decisiones o se impacienta debido a un perfeccionismo excesivo."),
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