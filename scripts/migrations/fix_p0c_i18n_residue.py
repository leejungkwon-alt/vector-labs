#!/usr/bin/env python3
"""scripts/migrations/fix_p0c_i18n_residue.py

결정론적 P0 잔존 (판단 불필요):
  A. ja/sections.json 'action' 제거 (en/zh_cn/es 스키마에 없음)
  B. zh_cn/monthly.json PEAK 문장 완역
  C. es/sections.json MODE_DISPLAY 전체 스페인어화
  D. es/core.json THE_BLADE/THE_DEEP name
  E. es: best_match/challenging_match 영문 모드명 → 스페인어
  F. es: GRADE_LABEL PEAK → Cumbre (7건)

실행:
  python scripts/migrations/fix_p0c_i18n_residue.py
  python scripts/migrations/fix_p0c_i18n_residue.py --apply
"""
from __future__ import annotations
import json, shutil, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "app" / "services" / "content" / "data"
APPLY = "--apply" in sys.argv
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

# ---- es MODE_DISPLAY (전체 스페인어화) ----
ES_MODE_DISPLAY = {
    "THE_STEWARD":    "Administrador",
    "THE_OPERATOR":   "Operador",
    "THE_FLOW":       "Flujo",
    "THE_CREATOR":    "Creador",
    "THE_CHALLENGER": "Desafiante",
    "THE_OFFICER":    "Guardián",
    "THE_SURVIVOR":   "Superviviente",
    "THE_MYSTIC":     "Místico",
    "THE_MENTOR":     "Mentor",
    "THE_GENERALIST": "Generalista",
    "THE_TWIN":       "Compañero",
    "THE_RIVAL":      "Rival",
    "THE_ALLY":       "Aliado",
    "THE_EMPATH":     "Empático",
    "THE_PIONEER":    "Pionero",
    "THE_ADAPTER":    "Adaptador",
    "THE_RADIATOR":   "Radiador",
    "THE_KEEPER":     "Linterna",
    "THE_ANCHOR":     "Ancla",
    "THE_CULTIVATOR": "Cultivador",
    "THE_BLADE":      "Filo",
    "THE_GEM":        "Gema",
    "THE_DEEP":       "Profundo",
    "THE_SPRING":     "Manantial",
}

# ---- en MODE_DISPLAY (역매핑용, en/sections.json 값) ----
EN_MODE_DISPLAY = {
    "THE_STEWARD": "Steward", "THE_OPERATOR": "Operator", "THE_FLOW": "Flow",
    "THE_CREATOR": "Creator", "THE_CHALLENGER": "Challenger", "THE_OFFICER": "Officer",
    "THE_SURVIVOR": "Survivor", "THE_MYSTIC": "Mystic", "THE_MENTOR": "Mentor",
    "THE_GENERALIST": "Generalist", "THE_TWIN": "Twin", "THE_RIVAL": "Rival",
    "THE_ALLY": "Ally", "THE_EMPATH": "Empath", "THE_PIONEER": "Pioneer",
    "THE_ADAPTER": "Adapter", "THE_RADIATOR": "Radiator", "THE_KEEPER": "Keeper",
    "THE_ANCHOR": "Anchor", "THE_CULTIVATOR": "Cultivator", "THE_BLADE": "Blade",
    "THE_GEM": "Gem", "THE_DEEP": "Deep", "THE_SPRING": "Spring",
}
EN_TO_ES_NAME = {EN_MODE_DISPLAY[k]: ES_MODE_DISPLAY[k] for k in EN_MODE_DISPLAY}

# ---- es GRADE_LABEL ----
ES_GRADE = {"PEAK": "Cumbre"}  # Favorable/Neutral/Precaución/Desafiante 이미 스페인어


def backup(p: Path) -> None:
    shutil.copy2(p, p.with_name(p.name + f".{TS}.bak"))


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def save(p: Path, data) -> None:
    if APPLY:
        backup(p)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ============================================================
# A. ja/sections.json — 'action' 제거
# ============================================================
def fix_ja_sections():
    p = DATA / "ja" / "sections.json"
    data = load(p)
    removed = 0
    for section in ("MONEY_CONTENT", "WORK_CONTENT", "BONDS_CONTENT"):
        blk = data.get(section, {})
        for k, v in blk.items():
            if isinstance(v, dict) and "action" in v:
                del v["action"]
                removed += 1
    if removed == 0:
        print("  ➖ ja/sections action: 이미 없음")
        return
    if APPLY:
        save(p, data)
    print(f"  {'✅' if APPLY else '🔍'} ja/sections action 제거: {removed}건")


# ============================================================
# B. zh_cn/monthly.json — PEAK 완역
# ============================================================
def fix_zh_monthly_peak():
    p = DATA / "zh_cn" / "monthly.json"
    data = load(p)
    ctx = data.get("MONTHLY_GRADE_CONTEXT", {})
    old = ctx.get("PEAK", "")
    # 'Root energy...' 로 시작하면 영어 잔존
    if not old.startswith("Root energy"):
        print(f"  ➖ zh_cn/monthly PEAK: 이미 완료 (현재: {old[:30]})")
        return
    ctx["PEAK"] = "本月底气（地支）顺畅，与主题无关。"
    if APPLY:
        save(p, data)
    print(f"  {'✅' if APPLY else '🔍'} zh_cn/monthly PEAK 번역")


# ============================================================
# C. es/sections.json MODE_DISPLAY 전체
# ============================================================
def fix_es_mode_display():
    p = DATA / "es" / "sections.json"
    data = load(p)
    md = data.get("MODE_DISPLAY", {})
    changed = 0
    for key, es_name in ES_MODE_DISPLAY.items():
        if key in md and md[key] != es_name:
            md[key] = es_name
            changed += 1
    if changed == 0:
        print("  ➖ es MODE_DISPLAY: 이미 완료")
        return
    data["MODE_DISPLAY"] = md
    if APPLY:
        save(p, data)
    print(f"  {'✅' if APPLY else '🔍'} es MODE_DISPLAY: {changed}건")


# ============================================================
# D. es/core.json ARCHETYPE name
# ============================================================
def fix_es_archetype_names():
    p = DATA / "es" / "core.json"
    data = load(p)
    changed = 0
    ac = data.get("ARCHETYPE_CONTENT", {})
    if ac.get("THE_BLADE", {}).get("name") == "El Blade":
        ac["THE_BLADE"]["name"] = "El Filo"
        changed += 1
    if ac.get("THE_DEEP", {}).get("name") == "El Deep":
        ac["THE_DEEP"]["name"] = "El Profundo"
        changed += 1
    if changed == 0:
        print("  ➖ es core.json archetype name: 이미 완료")
        return
    if APPLY:
        save(p, data)
    print(f"  {'✅' if APPLY else '🔍'} es core archetype name: {changed}건")


# ============================================================
# E. es 모든 파일의 best_match/challenging_match 영문 → 스페인어
# ============================================================
def walk_fix_names(obj, stats):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in ("best_match", "challenging_match") and isinstance(v, list):
                out[k] = []
                for name in v:
                    if isinstance(name, str) and name in EN_TO_ES_NAME:
                        out[k].append(EN_TO_ES_NAME[name])
                        stats["changed"] += 1
                    else:
                        out[k].append(name)
                        if isinstance(name, str) and name in EN_MODE_DISPLAY.values():
                            stats["unmapped"].add(name)
            else:
                out[k] = walk_fix_names(v, stats)
        return out
    if isinstance(obj, list):
        return [walk_fix_names(v, stats) for v in obj]
    return obj


def fix_es_best_match():
    stats = {"changed": 0, "unmapped": set()}
    es_dir = DATA / "es"
    files_changed = 0
    for fp in sorted(es_dir.rglob("*.json")):
        if fp.name == "sections.json":  # MODE_DISPLAY는 별도 처리
            continue
        data = load(fp)
        new = walk_fix_names(data, stats)
        if new != data:
            if APPLY:
                save(fp, new)
            files_changed += 1
    print(f"  {'✅' if APPLY else '🔍'} es best/challenging_match: {stats['changed']}건 ({files_changed} 파일)")
    if stats["unmapped"]:
        print(f"     ⚠️ 매핑 못한 영문명: {sorted(stats['unmapped'])}")


# ============================================================
# F. es GRADE_LABEL PEAK → Cumbre
# ============================================================
def walk_grade_fix(obj, stats):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in ("GRADE_LABEL", "GRADE_LABELS", "grade_labels") and isinstance(v, dict):
                out[k] = {}
                for gk, gv in v.items():
                    if gk in ES_GRADE and gv != ES_GRADE[gk]:
                        out[k][gk] = ES_GRADE[gk]
                        stats["changed"] += 1
                    else:
                        out[k][gk] = gv
            else:
                out[k] = walk_grade_fix(v, stats)
        return out
    if isinstance(obj, list):
        return [walk_grade_fix(v, stats) for v in obj]
    return obj


def fix_es_grade_labels():
    stats = {"changed": 0}
    es_dir = DATA / "es"
    files_changed = 0
    for fp in sorted(es_dir.rglob("*.json")):
        data = load(fp)
        new = walk_grade_fix(data, stats)
        if new != data:
            if APPLY:
                save(fp, new)
            files_changed += 1
    print(f"  {'✅' if APPLY else '🔍'} es GRADE_LABEL PEAK: {stats['changed']}건 ({files_changed} 파일)")


# ============================================================
def main() -> int:
    print("=" * 66)
    print(f"  fix_p0c_i18n_residue ({'APPLY' if APPLY else 'DRY-RUN'})")
    print("=" * 66)

    fix_ja_sections()
    fix_zh_monthly_peak()
    fix_es_mode_display()
    fix_es_archetype_names()
    fix_es_best_match()
    fix_es_grade_labels()

    print("=" * 66)
    if not APPLY:
        print("  dry-run 완료 → --apply 로 적용")
    else:
        print(f"  백업: *. {TS} .bak")
    print("=" * 66)
    return 0


if __name__ == "__main__":
    sys.exit(main())