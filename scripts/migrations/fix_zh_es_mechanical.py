"""
fix_zh_es_mechanical.py

남은 M-2 / M-3 / M-4 항목을 JSON-aware로 수정.
(문자열 부분 매칭이 아닌 정확한 값 매칭)
"""
import json
import pathlib

DATA = (pathlib.Path(__file__).resolve().parent
        / "app" / "services" / "content" / "data")


def _save(path: pathlib.Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def _walk_fix(obj, fix_map: dict, changes: list, path: str = ""):
    """dict/list를 순회하며 문자열 값을 fix_map에 따라 치환."""
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if isinstance(v, str) and v in fix_map:
                new = fix_map[v]
                changes.append(f"{path}.{k}: {v!r} -> {new!r}")
                obj[k] = new
            else:
                _walk_fix(v, fix_map, changes, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, str) and v in fix_map:
                new = fix_map[v]
                changes.append(f"{path}[{i}]: {v!r} -> {new!r}")
                obj[i] = new
            else:
                _walk_fix(v, fix_map, changes, f"{path}[{i}]")


# ── M-2: zh_cn 모드 레이블 정정 ──────────────────────
ZH_MODE_FIX = {
    "艾莉": "盟友",
    "警官": "管理者",
    "乘务员": "管家",
    "运营商": "运营者",
    "神秘": "神秘主义者",
    "双胞胎": "同伴者",
    # "流" 은 너무 흔한 글자라 값-정확 매칭 시에만 치환됨
    "流": "流动型",
}


def fix_zh_mode_labels() -> int:
    fixed = 0
    for fname in ("sections.json", "cross_insight.json",
                  "career.json", "wealth.json"):
        p = DATA / "zh_cn" / fname
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        changes = []
        _walk_fix(d, ZH_MODE_FIX, changes)
        if changes:
            _save(p, d)
            print(f"  [FIX]  zh_cn/{fname}")
            for c in changes:
                print(f"           {c}")
            fixed += len(changes)
    return fixed


# ── M-2 보강: zh_cn MODE_DISPLAY 누락 10개 추가 ─────
ZH_MODE_DISPLAY_ADD = {
    "THE_PIONEER":   "先锋 (Pioneer)",
    "THE_ADAPTER":   "适应者 (Adapter)",
    "THE_RADIATOR":  "太阳 (Radiator)",
    "THE_KEEPER":    "守灯人 (Keeper)",
    "THE_ANCHOR":    "锚 (Anchor)",
    "THE_CULTIVATOR":"耕耘者 (Cultivator)",
    "THE_BLADE":     "刀刃 (Blade)",
    "THE_GEM":       "宝石 (Gem)",
    "THE_DEEP":      "深海 (Deep)",
    "THE_SPRING":    "泉水 (Spring)",
}


def fix_zh_mode_display() -> int:
    p = DATA / "zh_cn" / "sections.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    md = d.setdefault("MODE_DISPLAY", {})
    added = 0
    for k, v in ZH_MODE_DISPLAY_ADD.items():
        if k not in md:
            md[k] = v
            added += 1
    # 기존 오역도 정리
    md.update({
        "THE_MYSTIC": "神秘主义者 (Mystic)",
        "THE_FLOW":   "流动型 (Flow)",
        "THE_TWIN":   "同伴者 (Twin)",
        "THE_OFFICER":"管理者 (Officer)",
        "THE_STEWARD":"管家 (Steward)",
        "THE_OPERATOR":"运营者 (Operator)",
        "THE_ALLY":   "盟友 (Ally)",
    })
    _save(p, d)
    print(f"  [FIX]  zh_cn/sections.json MODE_DISPLAY: +{added} added")
    return added


# ── M-3: es cross_insight MODE_LABELS / AXES ─────────
ES_MODE_LABELS = {
    "THE_TWIN":       "Compañero",
    "THE_RIVAL":      "Rival",
    "THE_ALLY":       "Aliado",
    "THE_EMPATH":     "Empático",
    "THE_CREATOR":    "Creador",
    "THE_CHALLENGER": "Desafiante",
    "THE_OFFICER":    "Guardián",
    "THE_SURVIVOR":   "Superviviente",
    "THE_MYSTIC":     "Místico",
    "THE_MENTOR":     "Mentor",
    "THE_GENERALIST": "Generalista",
    "THE_STEWARD":    "Administrador",
    "THE_OPERATOR":   "Operador",
    "THE_FLOW":       "Fluidez",
}

ES_AXES = {
    "DEPTH_BREADTH": {"pos": "Buceo profundo", "neg": "Amplia experiencia"},
    "STRUCTURE_FLOW": {"pos": "Reglas fijas", "neg": "Flujo improvisado"},
    "FREEDOM_BOND":   {"pos": "Unión",          "neg": "Soledad"},
    "RISK_SAFETY":    {"pos": "Nuevos desafíos","neg": "Base estable"},
    "EXPRESSION_RESTRAINT": {"pos": "Expresión", "neg": "Contención"},
    "COMPETITION_COLLABORATION": {"pos": "Competir", "neg": "Colaborar"},
    "SPEED_PATIENCE": {"pos": "Rapidez",         "neg": "Paciencia"},
    "SELF_OTHERS":    {"pos": "Yo primero",      "neg": "Los demás primero"},
}


def fix_es_cross_insight() -> int:
    p = DATA / "es" / "cross_insight.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["MODE_LABELS"] = ES_MODE_LABELS
    axes = d.setdefault("AXES", {})
    for k, v in ES_AXES.items():
        axes[k] = v
    _save(p, d)
    print(f"  [FIX]  es/cross_insight.json (MODE_LABELS 14, AXES {len(ES_AXES)})")
    return len(ES_MODE_LABELS) + len(ES_AXES)


# ── M-4: es element display 정정 ─────────────────────
ES_ELEMENT_FIX = {
    "Patada": "Chispa",
    "Flow":   "Flujo",
    "Suelo":  "Tierra",  # element "Tierra" 와 일치
    "Borde":  "Filo",    # "Metal/Filo" 개념 일치
}


def fix_es_elements() -> int:
    fixed = 0
    for fname in ("energy.json", "health.json", "sections.json",
                  "lucky_code.json", "core.json"):
        p = DATA / "es" / fname
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        changes = []
        _walk_fix(d, ES_ELEMENT_FIX, changes)
        # Cuatro 잔존 제거 (element 값일 때만)
        _walk_fix(d, {"Cuatro": "Fuego"}, changes)
        if changes:
            _save(p, d)
            print(f"  [FIX]  es/{fname}")
            for c in changes:
                print(f"           {c}")
            fixed += len(changes)
    return fixed


if __name__ == "__main__":
    print("── M-2: zh_cn 모드 레이블 정정 ──")
    n1 = fix_zh_mode_labels()
    print("\n── M-2: zh_cn MODE_DISPLAY 누락 보강 ──")
    n2 = fix_zh_mode_display()
    print("\n── M-3: es cross_insight ──")
    n3 = fix_es_cross_insight()
    print("\n── M-4: es element display ──")
    n4 = fix_es_elements()
    print(f"\n완료: M-2={n1}+{n2} / M-3={n3} / M-4={n4}")