#!/usr/bin/env python3
"""
Phase 4-B1: es/year.json YEAR_THEME_CONTENT 번역 (배치 1/5).
- TEN_GOD_FRIEND (3 variants)
- TEN_GOD_ROB_WEALTH (3 variants)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ES_YEAR = ROOT / "app" / "services" / "content" / "data" / "es" / "year.json"

TRANSLATIONS = {
    "TEN_GOD_FRIEND": [
        {
            "name": "La Narrativa de la Solidaridad y la Igualdad",
            "headline": "Este año, te convertirás en alguien que construye una comunidad sólida con colegas confiables.",
            "body": (
                "La narrativa central que recorre tu año no es un viaje solitario, sino la formación de un equipo sólido con personas que comparten tus metas. Te liberarás del peso que cargabas a solas y crearás alianzas horizontales que reconocen las fortalezas de cada uno.\n\n"
                "A través de este proceso, dejarás atrás la presión de liderar a otros y aprenderás la alegría de caminar lado a lado. La sinergia que se crea cuando personas que han dado lo mejor de sí en su propio lugar se encuentran es mucho más grande y cálida de lo que imaginas.\n\n"
                "El marco de solidaridad honesta que construyas a lo largo del año se convertirá en la cerca más fuerte que apoya tu vida. Apóyate en los hombros del otro y disfruta de un verdadero sentido de pertenencia y estabilidad.\n\n"
                "Será un tiempo valioso para darte cuenta de que llegar lejos juntos suele ser más valioso que ir rápido solo. Te animo a trazar una trayectoria de crecimiento brillante con las conexiones preciosas a tu lado."
            ),
            "watch_for": "Perder tu color único y tu subjetividad al dejarte arrastrar por la atmósfera del grupo.",
            "lean_into": "Construir una red de colegas centrales a largo plazo que respete la autonomía de cada uno.",
        },
        {
            "name": "Construyendo el Futuro Juntos",
            "headline": "Este año, te convertirás en un líder de la solidaridad que expande las metas personales hacia la sinergia colectiva.",
            "body": (
                "Este es el año para establecer un hito enorme con compañeros que se apoyan mutuamente en igualdad de condiciones. La calidez y autenticidad dentro de ti atraerán naturalmente a quienes te rodean y formarán una fuerza motriz enorme.\n\n"
                "Experimentarás la alegría de logros notables al compartir tareas a largo plazo que no te atrevías a hacer solo. A medida que completen las deficiencias del otro e intercambien inspiración, tu perspectiva se ampliará aún más.\n\n"
                "Durante este tiempo, compartir generosamente tu conocimiento y tu corazón se convierte en un atajo para elevar tu valor. El tiempo dedicado a reír y compartir preocupaciones con quienes te rodean se acumulará como tu activo más brillante.\n\n"
                "Un futuro construido juntos más allá del poder individual te da una emoción que hace latir el corazón. Abre tu corazón, extiende tu mano y da un paso poderoso hacia el éxito compartido."
            ),
            "watch_for": "Comprometer tus valores centrales con demasiada facilidad para evitar fricciones con quienes te rodean.",
            "lean_into": "Perseguir proyectos colaborativos a largo plazo con personas que comparten una visión común.",
        },
        {
            "name": "Estableciendo una Presencia Igualitaria",
            "headline": "A lo largo de este año, te convertirás en el centro de alianzas horizontales que intercambian una confianza profunda.",
            "body": (
                "Este es el año en que se completa una red de relaciones sana e igualitaria, donde puedes caminar lado a lado en cada espacio de tu vida. Renacerás como una persona experta que establece su presencia mientras reconoce de buen grado la autonomía de los demás.\n\n"
                "Dominarás profundamente cómo comunicarte en completa igualdad, rompiendo con las relaciones jerárquicas o las estructuras competitivas. Como resultado, desaparecen los malentendidos innecesarios y el agotador consumo emocional, reduciendo enormemente la fatiga de las relaciones.\n\n"
                "Las relaciones firmemente conectadas por una confianza profunda sin restringirse mutuamente son el tesoro más valioso que puedes ganar este año. Comparte conversaciones sinceras con quienes permanecen a tu lado y consolida los vínculos de sus corazones.\n\n"
                "La confianza mutua acumulada a lo largo del año aporta una enorme paz y orgullo a tu vida. Espero que disfrutes plenamente de la verdadera felicidad que florece en las relaciones equilibradas."
            ),
            "watch_for": "Sentir una impaciencia innecesaria al comparar tu velocidad de crecimiento con la de los demás.",
            "lean_into": "Invertir profundamente en relaciones igualitarias y honestas que se inspiren mutuamente.",
        },
    ],
    "TEN_GOD_ROB_WEALTH": [
        {
            "name": "El Filo Afilado",
            "headline": "Este año, serás entrenado hasta convertirte en un amo abrumador de la habilidad, inquebrantable ante cualquier estímulo externo.",
            "body": (
                "Este año se convierte en un poderoso campo de entrenamiento donde la competencia feroz y los estímulos externos despiertan tu potencial oculto. Una fuerte voluntad de superar los límites anteriores florece completamente dentro de ti, abriendo un dominio único.\n\n"
                "Los cambios rápidos o los entornos desafiantes a tu alrededor pueden sentirse abrumadores al principio, pero pronto se convierten en nutrientes que te hacen aún más fuerte. Experimentarás un crecimiento brillante al verificar objetivamente tus habilidades y llenar los vacíos.\n\n"
                "Al final del año, habiendo atravesado voluntariamente los feroces dolores del crecimiento, te erguirás como un árbol fuerte que nadie puede reemplazar. Disfruta de la emoción de demostrarte únicamente a través de tus habilidades, sin dejarte sacudir por el ruido externo.\n\n"
                "Adopta la mentalidad de afilar una hoja más dura cada vez que enfrentes una prueba. La ferocidad de este año se convertirá en tu mejor arma para hacerte brillar más en el día lejano."
            ),
            "watch_for": "Batallas de orgullo derrochadoras o gastos ostentosos para vencer a los demás.",
            "lean_into": "Convertir los estímulos competitivos externos únicamente en la fuerza motriz para fortalecer tus propias capacidades.",
        },
        {
            "name": "Custodiando la Soberanía",
            "headline": "Este año, renacerás como un líder subjetivo que controla perfectamente tu tiempo y tus recursos.",
            "body": (
                "El tema a largo plazo que recorre este año es establecer firmemente los límites de tu vida y recuperar completamente tu soberanía independiente. Entre demandas externas excesivas o luchas de poder, te darás cuenta claramente de qué valores necesitas proteger realmente.\n\n"
                "Practicarás no dejarte influir por las miradas o la interferencia de los demás y usar tu precioso tiempo y energía enteramente para ti. La sabiduría de trazar una línea firme cuando debas negarte se adquirirá naturalmente.\n\n"
                "Al organizar meticulosamente tu cerca a lo largo del año, completas una dignidad independiente que se yergue con orgullo ante la sacudida de los demás. Tendrás la emocionante experiencia de agarrar el volante de tu vida enteramente con tus propias manos.\n\n"
                "No desperdiciar energía en relaciones innecesarias o tareas agotadoras es la clave del éxito este año. Concéntrate solo en ti y en tu crecimiento, y construye un muro interior sólido."
            ),
            "watch_for": "Enredarte en luchas de poder agotadoras y evitables, desperdiciando recursos.",
            "lean_into": "Establecer límites claros y firmes para proteger tu energía y tus activos.",
        },
        {
            "name": "El Maestro del Avance",
            "headline": "A lo largo de este año, te convertirás en un pionero que rompe audazmente los límites y expande tu propio territorio.",
            "body": (
                "Este año es un año de crecimiento revolucionario en el que aprovechas al revés la tensión feroz y los entornos desafiantes para escribir tu propio mito. Rechazas la complacencia cómoda, te fijas estándares más altos y rompes los límites sin dudar.\n\n"
                "Cada vez que te topes con situaciones estancadas o muros altos, demostrarás la audacia de usarlos como trampolín para un salto adelante. Cuando otros dudan, das un paso adelante y haces tuyo el territorio de nuevas posibilidades.\n\n"
                "La tenacidad y la audacia firmemente establecidas a lo largo del año se convertirán en activos sin igual en el camino que recorrerás. La sensación de logro obtenida al atravesar el miedo de frente eleva tu autoestima al máximo.\n\n"
                "No definas tus propios límites y sal audazmente a un mundo más amplio. Verás la magia de las ambiciones que duermen dentro de ti transformándose en logros masivos del mundo real."
            ),
            "watch_for": "Tomar decisiones imprudentes e impulsivas arrastrado por la impaciencia o la ansiedad.",
            "lean_into": "Establecer metas elevadas y poner audazmente en acción tu impulso interior.",
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
        ("TEN_GOD_FRIEND", 0, "name", "La Narrativa de la Solidaridad y la Igualdad"),
        ("TEN_GOD_FRIEND", 2, "lean_into", "Invertir profundamente en relaciones igualitarias y honestas que se inspiren mutuamente."),
        ("TEN_GOD_ROB_WEALTH", 0, "name", "El Filo Afilado"),
        ("TEN_GOD_ROB_WEALTH", 2, "headline", "A lo largo de este año, te convertirás en un pionero que rompe audazmente los límites y expande tu propio territorio."),
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