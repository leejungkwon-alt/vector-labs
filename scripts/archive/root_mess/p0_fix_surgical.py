# p0_fix_surgical.py — P0 계약 위반 및 오역 4건 외과적 수정
# 실행: python p0_fix_surgical.py
# 재실행 안전(idempotent). 각 파일은 변경 전/후 diff를 출력.
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "app" / "services" / "content" / "data"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def fix_free_gating_timing(lang: str, wrong_value: str) -> bool:
    """zh_cn/es free_gating.json의 locked_hint_extra에서 wrong_value → 'timing'."""
    path = DATA / lang / "free_gating.json"
    if not path.exists():
        print(f"  ✗ {lang}/free_gating.json 없음")
        return False

    data = load(path)
    extra = data.get("locked_hint_extra", {})
    changed = False
    for section, hints in extra.items():
        if not isinstance(hints, list):
            continue
        for i, h in enumerate(hints):
            if h == wrong_value:
                hints[i] = "timing"
                print(f"  + {lang}: locked_hint_extra.{section}[{i}] '{wrong_value}' → 'timing'")
                changed = True

    # labels 키도 오염됐는지 확인 (timing 라벨은 번역된 값 유지, 키는 'timing'이어야 함)
    labels = data.get("labels", {})
    if "timing" not in labels:
        # 잘못된 키로 라벨이 들어가 있으면 이동
        for k in list(labels.keys()):
            if k in (wrong_value, "timing_" + lang):
                labels["timing"] = labels.pop(k)
                print(f"  + {lang}: labels '{k}' → 'timing'")
                changed = True

    if changed:
        save(path, data)
    return changed


def fix_zh_errors_dst_gap() -> bool:
    """zh_cn/errors.json의 DST_GAP 두 번째 {tz} → {clock}."""
    path = DATA / "zh_cn" / "errors.json"
    if not path.exists():
        print("  ✗ zh_cn/errors.json 없음")
        return False

    data = load(path)
    current = data.get("DST_GAP", "")
    # 정확히 두 개의 {tz}가 있고 {clock}이 한 번도 없는 경우만 수정
    if current.count("{tz}") == 2 and "{clock}" not in current:
        # 두 번째 {tz}를 {clock}으로
        first = current.index("{tz}")
        second = current.index("{tz}", first + 1)
        new = current[:second] + "{clock}" + current[second + len("{tz}"):]
        data["DST_GAP"] = new
        save(path, data)
        print(f"  + zh_cn/errors.json DST_GAP 수정")
        print(f"    before: {current}")
        print(f"    after : {new}")
        return True
    return False


def fix_es_cross_insight_collision() -> bool:
    """es/cross_insight.json COLLISION_SENTENCE / PULL_SENTENCE 오역 수정."""
    path = DATA / "es" / "cross_insight.json"
    if not path.exists():
        print("  ✗ es/cross_insight.json 없음")
        return False

    data = load(path)
    changed = False

    # KO: "{a_mode_label}의 '{a_label}'과 {b_mode_label}의 '{b_label}' 사이에서 흔들리고 있어요."
    # EN: wavering between the {a_mode_label}'s '{a_label}' and the {b_mode_label}'s '{b_label}'
    # 잘못된 ES: 'y los modelos «{b_mode_label}» y «{b_label}»' — 4개 항목으로 오독됨
    wrong_collision = "Estás dudando entre los modelos «{a_mode_label}» y «{a_label}», y los modelos «{b_mode_label}» y «{b_label}»."
    right_collision = "Estás dudando entre «{a_label}» de {a_mode_label} y «{b_label}» de {b_mode_label}."
    if data.get("COLLISION_SENTENCE") == wrong_collision:
        data["COLLISION_SENTENCE"] = right_collision
        print(f"  + es/cross_insight.json COLLISION_SENTENCE 재번역")
        changed = True

    # KO: "여기에 {mode_label}의 '{label}' 쪽으로 마음이 기울어요."
    # EN: your mind leans toward the {mode_label}'s '{label}'
    # 잘못된 ES: '«{label}» que por «{mode_label}»' — 비교 구문으로 오독
    wrong_pull = "Además, te inclinas más por el «{label}» que por el «{mode_label}»."
    right_pull = "Además, tu corazón se inclina hacia «{label}» de {mode_label}."
    if data.get("PULL_SENTENCE") == wrong_pull:
        data["PULL_SENTENCE"] = right_pull
        print(f"  + es/cross_insight.json PULL_SENTENCE 재번역")
        changed = True

    wrong_pull2 = "Y también se inclina hacia el «{label}» del {mode_label}."
    # 이건 의미상 OK이므로 손대지 않음

    if changed:
        save(path, data)
    return changed


def main() -> int:
    print("=" * 60)
    print(" P0 외과적 수정")
    print("=" * 60)

    changes = 0

    print("\n[1/3] free_gating.json locked_hint_extra — 'timing' 키 복원")
    if fix_free_gating_timing("zh_cn", "时机"):
        changes += 1
    if fix_free_gating_timing("es", "sincronización"):
        changes += 1

    print("\n[2/3] zh_cn/errors.json DST_GAP 템플릿")
    if fix_zh_errors_dst_gap():
        changes += 1

    print("\n[3/3] es/cross_insight.json COLLISION/PULL 문장")
    if fix_es_cross_insight_collision():
        changes += 1

    print("\n" + "=" * 60)
    if changes:
        print(f" 완료: {changes}개 항목 수정됨")
    else:
        print(" 변경 없음 (이미 수정됨)")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())