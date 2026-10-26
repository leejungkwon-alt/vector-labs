#!/usr/bin/env python3
"""
Phase 4-B5: es/year.json YEAR_THEME_CONTENT 번역 (배치 5/5).
- TEN_GOD_INDIRECT_RESOURCE (3 variants)
- TEN_GOD_DIRECT_RESOURCE (3 variants)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ES_YEAR = ROOT / "app" / "services" / "content" / "data" / "es" / "year.json"

TRANSLATIONS = {
    "TEN_GOD_INDIRECT_RESOURCE": [
        {
            "name": "La Visión de la Penetración Profunda",
            "headline": "Este año, te convertirás en un sabio que penetra la verdad oculta tras los fenómenos y dibuja el plano de la época.",
            "body": (
                "A lo largo de este año, te alejarás del ruido del mundo ruidoso y refinarás una sabiduría única y una visión aguda. Completarás una estrategia original a largo plazo captando los principios y patrones profundos de los eventos que otros no pueden ver.\n\n"
                "Tus ojos para penetrar el gran flujo de la época y la esencia sin dejarte influir por los fenómenos inmediatos se abren brillantemente. La comprensión obtenida a través de la profunda contemplación y la investigación diferencia completamente tu perspectiva.\n\n"
                "La sabiduría madurada profundamente en el interior a lo largo de un año se convertirá en un hito brillante en el camino que recorrerás. Filosofías originales y planes que el mundo admirará nacen en tu cabeza en este momento.\n\n"
                "Disfruta de la lectura tranquila y la contemplación y expande tu universo interior. La aguda visión que refinas este año se convierte en el arma más poderosa de tu vida en los años venideros."
            ),
            "watch_for": "Retrasar la ejecución práctica obsesionándote demasiado con los pensamientos y el análisis.",
            "lean_into": "Completar pensamientos conceptuales en informes estratégicos precisos o marcos originales.",
        },
        {
            "name": "La Fusión de la Intuición y la Sabiduría",
            "headline": "Este año, confiarás en tu aguda intuición interior y harás florecer una originalidad de nivel superior en el mundo.",
            "body": (
                "Este año es un año en el que la experiencia acumulada y la intuición profunda se combinan a la perfección para extraer una asombrosa visión intelectual. Resolverás claramente tareas complejas y enredadas con enfoques humanísticos y estratégicos que otros no pueden pensar fácilmente.\n\n"
                "Una inspiración intuitiva que trasciende los límites de la lógica destella, y encuentras las respuestas a problemas difíciles de inmediato. Tu perspectiva única y tus habilidades de interpretación profunda provocan la admiración de quienes te rodean.\n\n"
                "Al escuchar la voz interior a lo largo del año, se completa tu sabiduría única en el mundo. Tu experiencia y filosofía únicas dejan una marca clara en el mundo.\n\n"
                "Confía en la voz de la intuición que resuena dentro de ti y sumérgete en un aprendizaje profundo. Los logros intelectuales que acumulas este año se convierten en activos espirituales nobles que no se pueden comprar en ningún lugar."
            ),
            "watch_for": "Una tendencia a cortar la comunicación con los demás y aislarte demasiado en tu propio mundo.",
            "lean_into": "Asegurar tu propia experiencia original a través de la investigación profunda y la contemplación.",
        },
        {
            "name": "El Estratega que Lee el Futuro",
            "headline": "A lo largo de este año, te convertirás en alguien que abre nuevas oportunidades y dimensiones de la vida a través de la profunda contemplación.",
            "body": (
                "Este año es un año profundo para ampliar el horizonte del conocimiento, explorar los principios esenciales de la vida y lograr la madurez mental. Leerás el flujo del mundo con anticipación y completarás un plano de alta dimensión a través de un tiempo tranquilo de contemplación a solas.\n\n"
                "Diseñas de nuevo el tablero de la vida con un ojo macroscópico que mira varios pasos hacia adelante en lugar de perseguir ganancias inmediatas. La visión orientada al futuro que dibujas presenta una inspiración asombrosa a quienes te rodean.\n\n"
                "La aguda visión establecida a lo largo de un año se convierte en un faro que encuentra un camino incluso en cualquier crisis. Gracias a una excelente visión que parece predecir el futuro, cada elección da frutos precisos y brillantes.\n\n"
                "Tómate un tiempo para escapar del ruido del mundo y sumergirte en el pensamiento profundo y la investigación. El enorme plan maestro que estableces este año se convierte en una brújula sólida para guiar tu vida entera."
            ),
            "watch_for": "Comportarte en fantasías demasiado abstractas mientras ignoras las condiciones realistas.",
            "lean_into": "Acumular sabiduría que penetra la época a través del estudio profesional o la contemplación profunda.",
        },
    ],
    "TEN_GOD_DIRECT_RESOURCE": [
        {
            "name": "Recarga Abundante y Aceptación",
            "headline": "Este año, te convertirás en alguien que completa una poderosa fuerza interior a través del descanso sagrado y el aprendizaje.",
            "body": (
                "La narrativa a largo plazo que recorre este año es recuperar la fuerza física fundamental de la vida a través de la aceptación profunda y la recarga. Tendrás tiempo para absorber la sabiduría del maestro y consolar extremadamente tu cuerpo y mente cansados en lugar de correr sin aliento.\n\n"
                "Las capacidades internas llenadas paso a paso a lo largo de un año se convierten en la raíz más fuerte que apoya el salto a la siguiente etapa. Pon una coma elegante en tu vida que ha estado corriendo sin descanso y disfruta de una recuperación completa.\n\n"
                "Una actitud de soltar la impaciencia y absorber la sabiduría con un corazón humilde trae la mejor suerte. El descanso sagrado y la carga que disfrutas este año se convierten en una fuerza motriz masiva para un crecimiento explosivo en poco tiempo."
            ),
            "watch_for": "Perder la voluntad de liderar y ejecutar por tu cuenta al conformarte con una comodidad excesiva.",
            "lean_into": "Aprender humildemente la sabiduría del mentor y centrarte en una recuperación perfecta y una recarga interna.",
        },
        {
            "name": "El Sabio Beneficiario",
            "headline": "Este año, lograrás un descanso completo y crecimiento con el apoyo de cálidos ayudantes.",
            "body": (
                "Este año es un tiempo acogedor para aceptar humildemente la preciosa ayuda y el apoyo a tu alrededor y profundizar tu ser interior. Aprenderás a tratarte preciosamente a través del aprendizaje verificado y la tutoría, rompiendo con una vida de lucha solitaria.\n\n"
                "Conoces a un mentor o benefactor confiable que te aprecia y apoya, y obtienes lecciones preciosas de la vida. Encuentras paz mental al romper con la obsesión de que debes resolverlo todo con tus propias manos.\n\n"
                "Habiendo absorbido abundante amor y sabiduría a lo largo de un año, serás un árbol gigante que da consuelo a quienes te rodean. Logras un crecimiento seguro y certero dentro de la cálida cerca de los ayudantes.\n\n"
                "Demuestra la virtud de la aceptación aceptando plenamente el amor y el apoyo. El afectuoso cuidado y aprendizaje que disfrutas este año se convierten en la línea de vida más cálida y confiable que apoya tu vida."
            ),
            "watch_for": "Perder la independencia y la autonomía dependiendo demasiado del apoyo de los demás.",
            "lean_into": "Construir un entorno de aprendizaje óptimo y una rutina de recuperación sólida solo para ti.",
        },
        {
            "name": "La Finalización del Santuario Interior",
            "headline": "A lo largo de este año, renacerás como un maestro sabio con una resiliencia interior inquebrantable.",
            "body": (
                "Este año es un año pacífico para regresar al santuario interior, curar el alma cansada y compilar el know-how acumulado durante mucho tiempo. Priorizarás la estabilidad profunda del cuerpo y la mente y organizarás tus pensamientos cuidadosamente a través del aprendizaje.\n\n"
                "Construyes un santuario pacífico bloqueando los complejos ruidos externos y centrándote únicamente en la comunión profunda contigo mismo. Disfrutas de la bendición de que tu aprendizaje y experiencias se organicen en un sistema perfecto en tu cabeza.\n\n"
                "Después de un año, tu ser interior estará lleno de sabiduría profunda y confianza acogedora que no se tambalea en ninguna tormenta. La experiencia de curarte y consolarte completamente te convierte en un maestro que ejerce una buena influencia sobre los demás.\n\n"
                "Organiza tu conocimiento y cultiva firmemente el santuario de tu corazón. El santuario interior tranquilo y sólido que completas este año se convierte en el refugio más glorioso que te protege de por vida."
            ),
            "watch_for": "Complacencia que sigue posponiendo los desafíos reales con el pretexto de una preparación perfecta.",
            "lean_into": "Organizar sistemáticamente el conocimiento en manuales y activos para las generaciones futuras.",
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
        ("TEN_GOD_INDIRECT_RESOURCE", 0, "name", "La Visión de la Penetración Profunda"),
        ("TEN_GOD_INDIRECT_RESOURCE", 2, "lean_into", "Acumular sabiduría que penetra la época a través del estudio profesional o la contemplación profunda."),
        ("TEN_GOD_DIRECT_RESOURCE", 0, "name", "Recarga Abundante y Aceptación"),
        ("TEN_GOD_DIRECT_RESOURCE", 2, "headline", "A lo largo de este año, renacerás como un maestro sabio con una resiliencia interior inquebrantable."),
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