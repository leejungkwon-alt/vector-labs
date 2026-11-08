# scripts/translate_es.py
"""스페인어 timeline_themes.json 전체 번역 (KO 원본 기반)"""
import json
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
BASE = Path("app/services/content/data")

ES_THEMES = {
    "same": {
        "木": [
            {"theme": "Temporada de crecimiento continuo", "body": "La energía de crecimiento fluye durante toda la temporada. La misma dirección cansa — prueba nuevas formas a propósito."},
            {"theme": "Temporada de crecimiento profundo", "body": "La energía de crecimiento se hace más profunda. Enfócate en las raíces, no solo en los resultados visibles."},
            {"theme": "Temporada de crecimiento desbordado", "body": "El crecimiento se desborda. No intentes hacerlo todo a la vez — elige tus puntos."},
        ],
        "火": [
            {"theme": "Temporada de pasión constante", "body": "La pasión arde durante toda la temporada. El ritmo importa más que la intensidad."},
            {"theme": "Temporada de pasión profunda", "body": "La pasión se vuelve hacia adentro. Persigue lo que amas de verdad, no solo lo que brilla."},
            {"theme": "Temporada de pasión desbordada", "body": "Demasiadas cosas que quieres hacer. Elige una o dos — ahí llega el fruto."},
        ],
        "土": [
            {"theme": "Temporada de centro firme", "body": "La estabilidad fluye toda la temporada. Mantén pequeños cambios para no derivar."},
            {"theme": "Temporada de base construida", "body": "Los cimientos se afirman en lo invisible. No te apures — apila un ladrillo a la vez."},
            {"theme": "Temporada de raíces profundas", "body": "Las raíces se hunden bajo la superficie. El esfuerzo silencioso de hoy será fuerza duradera."},
        ],
        "金": [
            {"theme": "Temporada de juicio claro", "body": "La claridad se afila toda la temporada. Lo afilado corta — mantente suave donde importa."},
            {"theme": "Temporada de estándares claros", "body": "Tu sentido de lo correcto se agudiza. Eso sí, no pierdas flexibilidad."},
            {"theme": "Temporada de límites firmes", "body": "Se trazan líneas — mío vs. tuyo, sí vs. no. Esos límites te protegen."},
        ],
        "水": [
            {"theme": "Temporada de flexibilidad profunda", "body": "La flexibilidad se profundiza toda la temporada. Flotar demasiado pierde centro — haz pausas para reconectar."},
            {"theme": "Temporada de flujo amplio", "body": "La flexibilidad se extiende en muchas direcciones. Pero extenderse demasiado hace perder profundidad."},
            {"theme": "Temporada de nuevos cauces", "body": "Los flujos bloqueados se abren. Cuando aparezcan caminos nuevos, no pienses de más."},
        ],
    },
    "generates_me": {
        "木": [
            {"theme": "El crecimiento te empuja", "body": "La energía de crecimiento te empuja por detrás. Recibe — y luego pásalo."},
            {"theme": "El crecimiento te llena", "body": "El crecimiento te llena desde dentro. En la quietud plena, encuentra lo que quieres hacer."},
            {"theme": "El crecimiento te eleva", "body": "El crecimiento te eleva. Las semillas de ahora serán grandes árboles en pocos años."},
        ],
        "火": [
            {"theme": "La pasión te calienta", "body": "La pasión te envuelve con calidez. Expándete libremente esta temporada."},
            {"theme": "La pasión ilumina tu camino", "body": "La pasión ilumina el camino. Los lugares oscuros se vuelven visibles poco a poco."},
            {"theme": "La pasión te mueve", "body": "La pasión te mueve. Deja de pensar solo con la cabeza — mueve el cuerpo."},
        ],
        "土": [
            {"theme": "La estabilidad te sostiene", "body": "La estabilidad te sostiene con firmeza. Los movimientos audaces son seguros en este suelo."},
            {"theme": "La estabilidad te abraza", "body": "La estabilidad te abraza con calidez. Descansa cuando lo necesites."},
            {"theme": "La estabilidad te protege", "body": "La estabilidad te protege. Enfócate en conservar lo que tienes."},
        ],
        "金": [
            {"theme": "La claridad te refina", "body": "La claridad te refina. Las cosas borrosas se vuelven nítidas poco a poco."},
            {"theme": "La claridad te centra", "body": "La claridad te pone en tu centro. Lo que oscilaba se asienta."},
            {"theme": "La claridad te despierta", "body": "La claridad despierta lo dormido. Saca las decisiones que has estado posponiendo."},
        ],
        "水": [
            {"theme": "La flexibilidad te llena", "body": "La flexibilidad te llena. Una ayuda silenciosa llega de lugares inesperados."},
            {"theme": "La flexibilidad fluye en ti", "body": "La flexibilidad se mueve a través de ti. Los lugares atascados se desatascan solos."},
            {"theme": "La flexibilidad te limpia", "body": "La flexibilidad te limpia. Las emociones viejas se van y te sientes más ligero."},
        ],
    },
    "i_generate": {
        "木": [
            {"theme": "Tú haces crecer las cosas", "body": "Tú haces crecer cosas. Cuanto más das, más vuelve."},
            {"theme": "Tú nutres el crecimiento", "body": "Tú nutres cosas. La constancia acaba marcando la mayor diferencia."},
            {"theme": "Tú haces florecer", "body": "Tú haces florecer lo preparado. Lo que preparaste sale al mundo."},
        ],
        "火": [
            {"theme": "Tú creas fuego", "body": "Tú generas pasión. El trabajo creativo y expresivo brilla más."},
            {"theme": "Tú brillas fuerte", "body": "Tú brillas fuerte. Iluminas a quienes te rodean."},
            {"theme": "Tú compartes tu fuego", "body": "Tu pasión se extiende. El fuego compartido arde más grande."},
        ],
        "土": [
            {"theme": "Tú construyes cimientos", "body": "Tú pones el suelo. Los pequeños resultados se apilan uno a uno."},
            {"theme": "Tú apilas ladrillos", "body": "Tú apilas cosas con paciencia. Invisible ahora, firme después."},
            {"theme": "Tú afianzas tu suelo", "body": "Tú afianzas tu lugar en el mundo. Lo que oscilaba encuentra pie."},
        ],
        "金": [
            {"theme": "Tú marcas la dirección", "body": "Tú marcas la dirección. Los resultados sólidos empiezan a llegar."},
            {"theme": "Tú afinas las cosas", "body": "Tú afinas las cosas con cuidado. La precisión marca la diferencia."},
            {"theme": "Tú estableces estándares", "body": "Tú fijas estándares firmes. Ese estándar guiará los años venideros."},
        ],
        "水": [
            {"theme": "Tú abres caminos", "body": "Tú abres caminos nuevos. Crear flujo te lleva más lejos."},
            {"theme": "Tú creas el flujo", "body": "Tú creas el flujo mismo. Como el agua que cava un cauce, tú cavas el camino."},
            {"theme": "Tú conectas cosas", "body": "Tú conectas lo que estaba separado — personas, ideas, piezas."},
        ],
    },
    "i_control": {
        "木": [
            {"theme": "Tú manejas el crecimiento", "body": "La energía de crecimiento es fuerte. La ordenas y afirmas tu terreno."},
            {"theme": "Tú despejas espacio", "body": "Cortas el desorden para mantener dirección. Menos muestra más."},
            {"theme": "Tú agarras el crecimiento", "body": "Sostienes juntas las cosas dispersas. Ese agarre se vuelve fuerza."},
        ],
        "火": [
            {"theme": "Tú manejas el fuego", "body": "La energía de pasión es fuerte. La enfrías y das un paso atrás."},
            {"theme": "Tú calmas las cosas", "body": "Tú calmas lo que está caliente. Sabiduría para manejar el fuego."},
            {"theme": "Tú sostienes la llama", "body": "Tú manejas la llama. Bien manejada, se vuelve gran luz."},
        ],
        "土": [
            {"theme": "Tú manejas la estabilidad", "body": "La energía de estabilidad es fuerte. La moldeas y estabilizas el flujo."},
            {"theme": "Tú haces el suelo", "body": "Tú haces el suelo. Las cosas dispersas se juntan."},
            {"theme": "Tú agarras tierra firme", "body": "Te esfuerzas por no tambalearte. Ese agarre se vuelve tu centro."},
        ],
        "金": [
            {"theme": "Tú manejas la claridad", "body": "La energía de claridad es fuerte. Tu fuego la martilla en la forma que quieres."},
            {"theme": "Tú cortas limpio", "body": "Tú cortas lo que sobra. Lo que crece después del corte es más fuerte."},
            {"theme": "Tú sostienes el filo", "body": "Sostienes el filo firme. Un centro fuerte organiza lo que lo rodea."},
        ],
        "水": [
            {"theme": "Tú manejas la flexibilidad", "body": "La energía de flexibilidad es fuerte. La sostienes y te centras."},
            {"theme": "Tú agarras el flujo", "body": "Agarras cosas que fluyen. Agarra demasiado fuerte y el flujo se detiene."},
            {"theme": "Tú ordenas el flujo", "body": "Ordenas los flujos enredados. El flujo ordenado va más lejos."},
        ],
    },
    "controls_me": {
        "木": [
            {"theme": "El crecimiento te sacude", "body": "La energía de crecimiento te sacude. Cuanto más te prueba, más profundo echas raíces."},
            {"theme": "El crecimiento te refina", "body": "El crecimiento te refina. Aunque cueste, sales más firme."},
            {"theme": "El crecimiento te pone a prueba", "body": "El crecimiento pone a prueba tu límite. El muro de hoy es la puerta de mañana."},
        ],
        "火": [
            {"theme": "El fuego te templa", "body": "El fuego te templa. El calor te endurece, y eso es bueno."},
            {"theme": "El fuego te suaviza", "body": "El fuego suaviza tus bordes rugosos. La fricción es crecimiento."},
            {"theme": "El fuego te despierta", "body": "El fuego te despierta. La incomodidad es el inicio del cambio."},
        ],
        "土": [
            {"theme": "La estabilidad te contiene", "body": "La estabilidad te contiene. Las paredes te hacen ir más profundo."},
            {"theme": "La estabilidad te refina", "body": "La estabilidad te refina. El terreno conocido se vuelve trampolín."},
            {"theme": "La estabilidad te sostiene", "body": "La estabilidad te sostiene. Puede apretar — pero sostiene largo."},
        ],
        "金": [
            {"theme": "La claridad te corta", "body": "La claridad te corta. Lo que crece de vuelta es más fuerte."},
            {"theme": "La claridad te endereza", "body": "La claridad te endereza. Las cosas desordenadas se ordenan."},
            {"theme": "La claridad te pone a prueba", "body": "La claridad pone a prueba tu voluntad real. La respuesta ya está dentro de ti."},
        ],
        "水": [
            {"theme": "La flexibilidad te cubre", "body": "La flexibilidad te cubre. No te hundes — asciendes como vapor."},
            {"theme": "La flexibilidad te limpia", "body": "La flexibilidad te limpia. Lo viejo cae, la mente se aclara."},
            {"theme": "La flexibilidad te fluye", "body": "La flexibilidad te hace fluir. Suelta y deja que el flujo te lleve."},
        ],
    },
}

ES_CAUTIONS = {
    "same": {
        "danger": [
            "La misma dirección cansa rápido. Introduce estímulos nuevos a propósito.",
            "Puedes estancarte. Añade algo nuevo, aunque sea forzado.",
        ],
        "warning": [
            "Viene la complacencia. Prueba una cosa nueva a la vez.",
            "El aburrimiento se cuela. Haz pequeños cambios.",
        ],
        "neutral": [
            "Mantén el flujo, pero prepara un pequeño cambio.",
            "Tu ritmo está bien. Solo cuida la rutina.",
        ],
        "positive": [
            "Disfruta este grano. Las fuerzas en la misma dirección se empujan.",
            "Empápate. La energía similar te fortalece.",
        ],
    },
    "generates_me": {
        "danger": [
            "Solo recibir te adormece. Devuelve lo que recibes.",
            "Recibir de una sola vía agria. Pásalo.",
        ],
        "warning": [
            "Mientras te llenas, no olvides pasar lo recibido.",
            "Recibir solo te embota. Practica dar.",
        ],
        "neutral": [
            "Agradece y deja fluir.",
            "Equilibra recibir y dar.",
        ],
        "positive": [
            "Aprovecha este apoyo — se vuelve un gran salto.",
            "Saca el máximo de este impulso. Es ventana de lanzamiento.",
        ],
    },
    "i_generate": {
        "danger": [
            "Dar te agota. Llénate primero.",
            "Solo dar te vacía. Cuídate primero.",
        ],
        "warning": [
            "Revisa el equilibrio entre dar y recibir.",
            "Da — pero sin perderte.",
        ],
        "neutral": [
            "Da — pero sin pasar tu límite.",
            "Comparte con moderación. Dura más.",
        ],
        "positive": [
            "Cuanto más das, más te llenas. Comparte libre.",
            "Comparte tu abundancia. Crece.",
        ],
    },
    "i_control": {
        "danger": [
            "Apretar demasiado rompe el vínculo. Suelta lo que no puedes sostener.",
            "Agarra fuerte y se escapa. Tiempo de aflojar.",
        ],
        "warning": [
            "Maneja — no controles. Practica aflojar el agarre.",
            "El impulso de control sube. Haz una pausa.",
        ],
        "neutral": [
            "Maneja con suavidad y busca equilibrio.",
            "Tu ritmo está bien. Conserva flexibilidad.",
        ],
        "positive": [
            "Tu manejo está bien ahora. Mantén este paso.",
            "Esta afinación es perfecta. Recuerda esta sensación.",
        ],
    },
    "controls_me": {
        "danger": [
            "La presión alimenta urgencia. No corras contra el ritmo ajeno.",
            "No es momento de empujar. Deja que la corriente te lleve.",
        ],
        "warning": [
            "No resistas ahora — deja que la corriente te lleve.",
            "Aceptar funciona mejor que resistir aquí.",
        ],
        "neutral": [
            "Reconoce la presión, mantén tu paso.",
            "Deja fluir — pero sin perder centro.",
        ],
        "positive": [
            "Un poco de presión es combustible para crecer.",
            "Usa esta presión como combustible. Grandes saltos vienen de aquí.",
        ],
    },
}

ES_PRACTICES = {
    "same": {
        "danger": [
            "Mantén la forma actual — pero cambia una cosa a propósito.",
            "Empieza pequeño: un cambio al día.",
        ],
        "warning": [
            "Prueba algo nuevo por trimestre.",
            "Una vez al mes, elige diferente.",
        ],
        "neutral": [
            "Prueba un enfoque nuevo cada año.",
            "Añade estímulo nuevo cada trimestre.",
        ],
        "positive": [
            "Disfruta el ritmo y estira más esa fortaleza.",
            "Lleva este flujo al siguiente nivel.",
        ],
    },
    "generates_me": {
        "danger": [
            "Pásalo. Si no, te adormeces.",
            "Registra lo recibido — y devuélvelo.",
        ],
        "warning": [
            "Muestra gratitud por lo recibido — con palabras o actos.",
            "Comparte un poco de lo recibido.",
        ],
        "neutral": [
            "Registra lo que recibes. Devuélvelo como gratitud.",
            "Comparte tus ganancias en pequeño.",
        ],
        "positive": [
            "Aprovecha este apoyo. Es ventana de expansión.",
            "Aplica este impulso a una meta grande. Semilla de salto.",
        ],
    },
    "i_generate": {
        "danger": [
            "Llénate primero. No es temporada de dar — es de rellenar.",
            "Un día a la semana, todo para ti.",
        ],
        "warning": [
            "Revisa una vez el equilibrio entre dar y recibir.",
            "Antes de dar, revisa tu propia taza.",
        ],
        "neutral": [
            "Guarda un día completo a la semana solo para ti.",
            "Protege tiempo para rellenarte tanto como das.",
        ],
        "positive": [
            "Da libre. Cuanto más das, más te llenas.",
            "Pasa esta abundancia. Se multiplica.",
        ],
    },
    "i_control": {
        "danger": [
            "Practica soltar — una cosa al día.",
            "Hoy, deja fluir una decisión.",
        ],
        "warning": [
            "Afloja el agarre. Maneja — no controles.",
            "Antes de decidir, pregúntate: '¿De verdad necesito sostener esto?'",
        ],
        "neutral": [
            "Antes de decidir, pregúntate: '¿Realmente necesito controlar esto?'",
            "Una vez al día, nota el impulso de controlar.",
        ],
        "positive": [
            "Mantén esta sensación. Estás en buen ritmo.",
            "Anota este ritmo — reutilízalo después.",
        ],
    },
    "controls_me": {
        "danger": [
            "Protege tu ritmo. No corras contra el ritmo ajeno.",
            "5 minutos al día: respira y sigue la corriente.",
        ],
        "warning": [
            "Reduce resistencia. Deja que la corriente te lleve.",
            "Una vez al día, acepta lo que no puedes controlar.",
        ],
        "neutral": [
            "Construye una habilidad al año que dure la próxima década.",
            "Un día a la semana, sin planes.",
        ],
        "positive": [
            "Convierte la presión en combustible. Es tu motor de crecimiento.",
            "Usa esta presión como peldaño al siguiente nivel.",
        ],
    },
}

ES_ELEM = {"木": "crecimiento", "火": "pasión", "土": "estabilidad", "金": "claridad", "水": "flexibilidad"}

data = {
    "THEMES": ES_THEMES,
    "CAUTIONS": ES_CAUTIONS,
    "PRACTICES": ES_PRACTICES,
    "ELEM_LABEL": ES_ELEM,
}

out = BASE / "es" / "timeline_themes.json"
out.parent.mkdir(parents=True, exist_ok=True)

if APPLY:
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ es: {out}")
else:
    print(f"🧪 미리보기: {out}")
    print("🧪 미리보기. 적용: python scripts/translate_es.py --apply")