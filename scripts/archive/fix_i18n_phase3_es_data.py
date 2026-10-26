#!/usr/bin/env python3
"""
Phase 3: data/es/ 우선순위 팩 5개 생성.
- en 팩을 복제한 뒤 우선순위 키만 스페인어로 오버라이드
- 나머지 키는 영어 유지 (Phase 4 대상, 복사본 내 영어 → es 리포트에 영어로 노출됨)
- es/{core,energy,sinsal,health,...}.json 은 만들지 않음 → 로더가 en으로 per-file 폴백

이유: loader.load_pack은 per-file 폴백. es/sections.json이 일부 키만 있으면
누락 키는 빈 dict가 됨. 따라서 완전 복제 후 오버라이드가 안전.
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# verify() 안에서 `from app...` import가 되도록 — 재실행 시 안전
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
DATA = ROOT / "app" / "services" / "content" / "data"
EN = DATA / "en"
ES = DATA / "es"

errors, written, skipped = [], [], []

# ---------------- translations ----------------

ERRORS_ES = {
    "DST_AMBIGUOUS": (
        "Esta hora es ambigua: {clock} ocurre dos veces en {tz}. "
        "Vuelve a solicitar con dst_fold=0 (offset {off0}) o "
        "dst_fold=1 (offset {off1})."
    ),
    "DST_GAP": (
        "Esta hora no existe: {clock} es omitida por el horario de verano en {tz}."
    ),
}

DAEWOON_ES = {
    "DISPLAY_TPL": "{years} años {months} meses",
    "CORRECTION_TPL": " (corregido a la edad de inicio {start_age})",
}

YEAR_OVERRIDE_ES = {
    "DEFAULT_YEAR_THEME": {
        "name": "El Año en Desarrollo",
        "headline": "Un año que aún toma forma.",
        "body": (
            "La energía de este año es difícil de reducir a un solo patrón. "
            "Presta atención — el tema se revelará a medida que avances."
        ),
        "watch_for": "Asumir que ya sabes de qué trata este año.",
        "lean_into": "Mantener la curiosidad sobre lo que realmente está sucediendo.",
    },
    "SOLAR_CALENDAR_NOTE": (
        "El año de arriba sigue el calendario de términos solares "
        "(Lichun a Lichun). En enero, el año solar anterior aún está activo."
    ),
}

SECTIONS_OVERRIDE_ES = {
    "SECTION_TITLES": {
        "cover": "Tu Carta",
        "core": "Tu Núcleo",
        "energy": "Tu Firma Energética",
        "lucky_code": "Tu Código de Suerte",
        "health": "Cuerpo y Bienestar",
        "money": "Dinero y Riqueza",
        "work": "Trabajo y Oficio",
        "bonds": "Vínculos y Pertenencia",
        "year": "Este Año",
        "timeline": "Tu Línea de Tiempo",
        "monthly": "Tu Calendario Mensual",
        "chart": "Tus Cuatro Rostros",
        "sinsal": "Rasgos Especiales",
    },
    "SUMMARY_LABELS": {
        "core": "Núcleo",
        "energy": "Energía",
        "lucky_code": "Código",
        "money": "Modo Dinero",
        "bonds": "Vínculos",
        "year": "Este Año",
        "health": "Cuerpo",
        "monthly": "Mensual",
    },
    "INTENSITY_LABELS": {
        "SELF_SOURCED": "Autoabastecido",
        "BALANCED_CORE": "Núcleo Equilibrado",
        "ENVIRONMENT_TUNED": "Sintonizado con el Entorno",
    },
    "ENERGY_HERO_TEMPLATES": {
        "missing": "Funcionas con {dominant} — casi sin {missing}.",
        "deficient": (
            "Lideras con {dominant}, pero llevas una escasez silenciosa "
            "de {deficient}."
        ),
        "default": "Funcionas con {dominant}.",
    },
    "TIMELINE_HERO": (
        "Tu década más fuerte comienza alrededor de los {best_age} años "
        "({best_pillar}). La más desafiante comienza alrededor de "
        "los {worst_age} años."
    ),
    "TIMELINE_GRADE_BLURB": {
        "PEAK": "Una ventana rara. Úsala deliberadamente.",
        "FAVORABLE": "Vientos a favor. Muévete con ellos.",
        "NEUTRAL": "Mixto. Presta atención a lo que realmente funciona.",
        "CAUTION": "Temporada más lenta. Prioriza el descanso y los límites.",
        "CHALLENGING": "Período pesado. Sobrevívelo bien y crecerás.",
    },
    "LUCKY_CODE_HERO_TEMPLATE": (
        "Tu elemento de poder es {element} — apóyate en él."
    ),
    "WATCH_OUT_LABEL": "Atención",
    "HEALTH_HERO_TEMPLATES": {
        "missing": "{dominant} domina — casi no tienes {missing}.",
        "deficient": "{dominant} te moldea más; {deficient} escasea.",
        "default": "{dominant} te moldea.",
    },
    "CHART_POSITION_TEMPLATES": {
        "year_pillar": (
            "En tus orígenes, {archetype} moldeó cómo conociste el mundo."
        ),
        "month_pillar": (
            "En tu trabajo público, {archetype} es cómo te presentas."
        ),
        "day_pillar": "{archetype} es tu núcleo — esto es quién eres.",
        "hour_pillar": (
            "En tu legado, {archetype} definirá lo que dejas atrás."
        ),
    },
    "CHART_NOTE_TEMPLATE": (
        "Tu {a} y tu {b} comparten la misma energía '{archetype}'. "
        "Esto significa que son inseparables — tu vida pública y tu núcleo son uno."
    ),
    "DISCLAIMER": (
        "Nota: Este informe combina cálculos astronómicos con marcos modernos "
        "de coaching para la percepción personal y el entretenimiento. No es "
        "consejo médico, financiero ni psicológico. El análisis tradicional de "
        "Cuatro Pilares depende de la escuela — distintas líneas pueden llegar "
        "a conclusiones diferentes a partir de la misma carta, del mismo modo "
        "que distintos terapeutas pueden describir a la misma persona de forma "
        "diferente. Trátalo como una lectura reflexiva, no como un veredicto. "
        "Tus decisiones siguen siendo tuyas. Si estás en crisis, contacta a los "
        "servicios de emergencia locales o a una línea de prevención del "
        "suicidio. Si estás fuera de EE. UU., consulta "
        "https://findahelpline.com/."
    ),
}

LABELS_OVERRIDE_ES = {
    "BALANCE_LABEL": "equilibrio",
    "CHART_HERO": "Tu plano, expresado como cuatro rostros.",
    "CHART_LAYER_META": {
        "year_pillar": {
            "label": "Infancia",
            "role": "Tus raíces — cómo empezaste y la influencia familiar",
        },
        "month_pillar": {
            "label": "Carrera",
            "role": "Tu vida social — cómo trabajas e interactúas",
        },
        "day_pillar": {
            "label": "Núcleo",
            "role": "Tu identidad verdadera — quién eres en esencia",
        },
        "hour_pillar": {
            "label": "Futuro",
            "role": "Tu mundo interior — tus sueños y tus años posteriores",
        },
    },
    "SINSAL_POS_LABEL": {
        "year_pillar": "Orígenes",
        "month_pillar": "Carrera",
        "day_pillar": "Ser",
        "hour_pillar": "Legado",
    },
    "SINSAL_POS_ROLE": {
        "year_pillar": "ancestros y entorno temprano",
        "month_pillar": "carrera y vida pública",
        "day_pillar": "ser y pareja",
        "hour_pillar": "mundo interior y legado",
    },
    "SINSAL_THEME_KEYWORD": {
        "MAGNETIC_DRAW": "magnetismo y atracción",
        "RESTLESS_FEET": "movimiento y exploración",
        "SOLITARY_DEPTH": "reflexión y creatividad",
        "ALLY_MAGNET": "ayuda y apoyo",
        "SCHOLAR_MIND": "estudio y aprendizaje",
        "SHARP_EDGE": "impulso y competencia",
        "COMMANDER": "liderazgo y decisión",
    },
    "SINSAL_NOTE_TPL": (
        "Este rasgo se sitúa en tu {role} — por eso {theme} se manifiesta "
        "más en esa área."
    ),
    "SINSAL_HERO_ONE": "Llevas 1 rasgo especial.",
    "SINSAL_HERO_MANY": "Llevas {n} rasgos especiales.",
    "GRADE_LABELS": {
        "PEAK": "Cúspide",
        "FAVORABLE": "Favorable",
        "NEUTRAL": "Neutral",
        "CAUTION": "Precaución",
        "CHALLENGING": "Desafiante",
    },
    "COMPAT_FALLBACK_HEADLINE": "Una relación que construyen juntos.",
}


# ---------------- helpers ----------------

def write_json(path: Path, data: dict) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    try:
        json.loads(payload)
    except json.JSONDecodeError as e:
        print(f"  [ERR] {path.name}: JSON 유효성 실패 ({e})")
        errors.append(path.name)
        return False
    path.write_text(payload, encoding="utf-8")
    print(f"  [OK] {path.name}")
    written.append(path.name)
    return True


def copy_en_to_es(name: str) -> dict:
    src = EN / name
    dst = ES / name
    if not src.exists():
        print(f"  [ERR] en/{name} 없음")
        errors.append(f"copy {name}")
        return {}
    if dst.exists():
        print(f"  [SKIP] es/{name} 이미 존재 — 그대로 사용")
        skipped.append(name)
    else:
        shutil.copy2(src, dst)
        print(f"  [OK] es/{name} ← en/{name}")
    return json.loads(dst.read_text(encoding="utf-8"))


def override_and_write(name: str, override: dict) -> None:
    data = copy_en_to_es(name)
    if not data:
        return
    data.update(override)
    write_json(ES / name, data)


# ---------------- phases ----------------

def phase1_errors():
    print("\n[1/5] errors.json (전면 스페인어)")
    ES.mkdir(parents=True, exist_ok=True)
    write_json(ES / "errors.json", ERRORS_ES)


def phase2_daewoon():
    print("\n[2/5] daewoon.json (전면 스페인어)")
    write_json(ES / "daewoon.json", DAEWOON_ES)


def phase3_year():
    print("\n[3/5] year.json (en 복제 + DEFAULT_YEAR_THEME + SOLAR_CALENDAR_NOTE 오버라이드)")
    override_and_write("year.json", YEAR_OVERRIDE_ES)


def phase4_labels():
    print("\n[4/5] labels.json (en 복제 + 우선순위 키 오버라이드)")
    override_and_write("labels.json", LABELS_OVERRIDE_ES)


def phase5_sections():
    print("\n[5/5] sections.json (en 복제 + 섹션 제목/디스클레이머 오버라이드)")
    override_and_write("sections.json", SECTIONS_OVERRIDE_ES)


# ---------------- verification ----------------

def verify():
    print("\n[verify] 로드 및 오버라이드 확인")
    from app.services.content.loader import load_pack
    ok = True

    # 1) errors
    e = load_pack("es", "errors")
    if "ocurre dos veces" in e.get("DST_AMBIGUOUS", ""):
        print("  [OK] errors.json → Spanish")
    else:
        print(f"  [ERR] errors.json: {e.get('DST_AMBIGUOUS', '')[:60]}")
        ok = False

    # 2) daewoon
    d = load_pack("es", "daewoon")
    if "años" in d.get("DISPLAY_TPL", ""):
        print("  [OK] daewoon.json → Spanish")
    else:
        print(f"  [ERR] daewoon: {d}")
        ok = False

    # 3) year
    y = load_pack("es", "year")
    if "calendario de términos solares" in y.get("SOLAR_CALENDAR_NOTE", ""):
        print("  [OK] year.json → SOLAR_CALENDAR_NOTE Spanish")
    else:
        print(f"  [ERR] year SOLAR_CALENDAR_NOTE: {y.get('SOLAR_CALENDAR_NOTE', '')[:60]}")
        ok = False
    if y.get("DEFAULT_YEAR_THEME", {}).get("name") == "El Año en Desarrollo":
        print("  [OK] year.json → DEFAULT_YEAR_THEME Spanish")
    else:
        print("  [ERR] year DEFAULT_YEAR_THEME name mismatch")
        ok = False
    # year content은 여전히 영어 (Phase 4 대상)
    if "YEAR_THEME_CONTENT" in y and "TEN_GOD_FRIEND" in y["YEAR_THEME_CONTENT"]:
        print("  [OK] year.json → YEAR_THEME_CONTENT 영어 유지 (Phase 4)")

    # 4) labels
    L = load_pack("es", "labels")
    if L.get("GRADE_LABELS", {}).get("PEAK") == "Cúspide":
        print("  [OK] labels.json → GRADE_LABELS Spanish")
    else:
        print(f"  [ERR] labels GRADE_LABELS PEAK: {L.get('GRADE_LABELS', {}).get('PEAK')}")
        ok = False

    # 5) sections
    s = load_pack("es", "sections")
    if s.get("SECTION_TITLES", {}).get("core") == "Tu Núcleo":
        print("  [OK] sections.json → SECTION_TITLES Spanish")
    else:
        print(f"  [ERR] sections SECTION_TITLES.core: {s.get('SECTION_TITLES', {}).get('core')}")
        ok = False
    if "informe combina cálculos astronómicos" in s.get("DISCLAIMER", ""):
        print("  [OK] sections.json → DISCLAIMER Spanish")
    else:
        print(f"  [ERR] sections DISCLAIMER not Spanish: {s.get('DISCLAIMER', '')[:60]}")
        ok = False
    # MONEY_CONTENT 영어 유지 (per-file 폴백 함정 회피 검증)
    if "MONEY_CONTENT" in s and "THE_STEWARD" in s["MONEY_CONTENT"]:
        print("  [OK] sections.json → MONEY_CONTENT 보존 (English, Phase 4)")
    else:
        print("  [ERR] sections MONEY_CONTENT missing — es money 섹션이 비게 됨")
        ok = False

    # 6) 미생성 팩은 en 폴백 확인
    core = load_pack("es", "core")
    if core.get("ARCHETYPE_CONTENT", {}).get("THE_PIONEER", {}).get("name") == "The Pioneer":
        print("  [OK] core.json → en 폴백 (per-file fallback)")
    else:
        print("  [ERR] core.json fallback broken")
        ok = False

    return ok


def main() -> int:
    print("=" * 60)
    print("[Phase 3] data/es/ 우선순위 팩 5개")
    print("=" * 60)

    phase1_errors()
    phase2_daewoon()
    phase3_year()
    phase4_labels()
    phase5_sections()

    ok = verify()

    print("\n" + "=" * 60)
    print(f"결과: written {len(written)} / skipped {len(skipped)} / errors {len(errors)}")
    print("=" * 60)

    if ok and not errors:
        print("\n[Phase 3 OK] 다음 커맨드:")
        print("  python -m pytest -q")
        print("  cd frontend; npx tsc --noEmit; cd ..")
        print('  git add -A; git commit -m "feat(i18n): es data packs (priority overrides)"')
        return 0
    print(f"\n[Phase 3 FAIL] errors {len(errors)} — 위 로그 확인")
    return 1


if __name__ == "__main__":
    sys.exit(main())