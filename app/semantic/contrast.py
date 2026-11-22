# app/semantic/contrast.py
"""사주 × MBTI **대조(contrast)** 판정 — 순수 함수.

⚠️ 이것은 측정이 아니라 **해석 장치**다.

  여기의 점수는 사람의 성격을 "재는" 값이 아니다. 사주 태그(신강/신약·신살·
  격국·오행 분포)를 `outward / inward` 라는 두 개의 **해석 렌즈**에 비추어
  "이 원국을 바깥으로 뻗는 결로 읽을 수 있는가, 안으로 모으는 결로 읽을 수
  있는가"를 요약한 **편의 지표**일 뿐이다.
  - 명리 안에서도 신강/신약·격국 판정은 학파에 따라 달라진다.
  - 그러므로 이 값은 진단·검사·예측이 아니며, 어떤 식으로도 단정하지 않는다.

출력 계약
  결과는 `outward` | `inward` | `balanced` **세 값 중 하나**뿐이다.
  MBTI 4글자 유형을 추정하거나 만들어내지 않는다. MBTI 는 사용자가 스스로
  입력한 값과 "대조"할 뿐, 이 모듈이 유형을 산출하지 않는다.

시주(時柱) 의존 신호
  시각을 모르면(noon 가정 / day_only) 신강·오행 분포·시지 기반 신살·충이
  흔들린다. 그래서 그런 신호는 **감쇠가 아니라 점수에서 제외**하고
  `hour_signals_excluded = True` 로 알린다.
"""

from app.engine.elements import analyze_element_distribution
from app.engine.gyeokguk import determine_gyeokguk
from app.engine.relations import detect_relations, summarize_relations
from app.engine.sinsal import detect_sinsal
from app.engine.strength import assess_day_master_strength
from app.engine.yongsin import derive_useful_god

# ============================================================
# 신호 정의  (가중치, 시주 의존 여부)
# ============================================================
# outward / inward 대칭 원칙: 같은 계열은 같은 가중치.
SIGNAL_WEIGHTS = {
    # ---- outward ----
    "S1_STRONG_DAY_MASTER": (3, True),    # 신강
    "S2_YEOKMA":            (3, True),    # 역마 (시지 단독 hit 은 제외)
    "S3_DAY_CHONG":         (2, False),   # 일지 충
    "S4_HAS_CHONG":         (2, True),    # 충 존재 (시지 관여 충은 제외)
    "S6_GWEGANG":           (3, False),   # 괴강
    "S7_YANGIN":            (2, False),   # 양인
    "S8_SANGGWAN":          (3, False),   # 상관격
    "S9_PYEONGWAN":         (3, False),   # 편관격
    "S12_CHALLENGER":       (2, False),   # work_mode=THE_CHALLENGER
    "S13_FIRE_DOMINANT":    (2, True),    # 火 과다
    "S14_WOOD_DOMINANT":    (2, True),    # 木 과다
    "S15_EARTH_DEFICIENT":  (2, True),    # 土 결핍
    "S16_YONGSIN_EXPRESS":  (2, True),    # 용신=식상(신강 조건)
    # ---- inward ----
    "N1_HWAGAE":            (3, True),    # 화개 (시지 단독 hit 은 제외)
    "N2_WEAK_DAY_MASTER":   (3, True),    # 신약
    "N3_FIRE_DEFICIENT":    (2, True),    # 火 결핍
    "N4_METAL_DEFICIENT":   (2, True),    # 金 결핍
    "N5_WATER_DEFICIENT":   (2, True),    # 水 결핍
    "N6_JEONGGWAN":         (2, False),   # 정관격
    "N7_DAY_HE":            (2, False),   # 일지 합
}

# 중립(점수 0)으로 확정된 신호와 이유.
#  S5 도화: 매력이 주체일 때도 대상일 때도 성립(양방향).
#  S10 건록격: "자립"(안)과 "추진"(밖)이 동시에 읽힘.
#  S11 편재격: E/I 축이 아니라 J/P 축 후보 — 신호에서 **제거**.
#  S17 양간 아키타입: 음양 쌍(丙/丁, 甲/乙 …)이 곧 대칭축이라 한쪽 고정 불가.
NEUTRAL_SIGNALS = {
    "S5_DOHWA": "양방향(주체/대상) 해석 모두 성립",
    "S10_GEONROK": "자립(안)과 추진(밖) 이중 해석",
    "S17_YANG_STEM": "음양 쌍이 대칭축이라 방향 고정 불가",
}
# S11 편재격은 E/I 신호가 아니므로 신호 목록에서 제외(3단계 확정 결정).
REMOVED_SIGNALS = {"S11_PYEONJAE": "E/I 축이 아닌 J/P 후보 — 제거"}

# 같은 계열 동시 발동 시 최댓값만 합산(중복 가산 방지)
_SIGNAL_GROUPS = (
    frozenset({"S3_DAY_CHONG", "S4_HAS_CHONG"}),
    frozenset({"S6_GWEGANG", "S7_YANGIN", "S9_PYEONGWAN", "S12_CHALLENGER"}),
    frozenset({"S8_SANGGWAN", "S16_YONGSIN_EXPRESS", "S14_WOOD_DOMINANT"}),
)

# balanced 임계(T1) 및 절대량 가드
BALANCED_LOW = 0.35
BALANCED_HIGH = 0.65
MIN_SIGNAL_MASS = 4  # OUT + IN 이 이보다 작으면 balanced

LABELS = ("outward", "inward", "balanced")


def _hit_positions(entries):
    """detect_sinsal 결과의 위치 집합."""
    return {e.get("position") for e in (entries or []) if isinstance(e, dict)}


def _only_hour_position(entries):
    """시지에서만 잡힌 신살인지(시각 미상이면 사라지는 신호)."""
    positions = _hit_positions(entries)
    return bool(positions) and positions == {"hour_pillar"}


def _sum_with_decay(signal_ids):
    """계열 내 중복을 최댓값으로 접어 outward/inward 점수를 낸다."""
    out_score = 0
    in_score = 0
    remaining = set(signal_ids)
    for group in _SIGNAL_GROUPS:
        hits = remaining & group
        if not hits:
            continue
        # 그룹당 하나만 살린다: 가중치가 가장 큰 신호(동률이면 id 순)
        best = max(hits, key=lambda s: (SIGNAL_WEIGHTS[s][0], s))
        remaining -= hits
        if best.startswith("S"):
            out_score += SIGNAL_WEIGHTS[best][0]
        else:
            in_score += SIGNAL_WEIGHTS[best][0]
    for sid in remaining:
        weight = SIGNAL_WEIGHTS[sid][0]
        if sid.startswith("S"):
            out_score += weight
        else:
            in_score += weight
    return out_score, in_score


def label_for(out_score: int, in_score: int) -> str:
    """점수 → 라벨. balanced 임계 T1 + 절대량 가드."""
    total = out_score + in_score
    if total < MIN_SIGNAL_MASS:
        return "balanced"
    out_share = out_score / total
    if out_share > BALANCED_HIGH:
        return "outward"
    if out_share < BALANCED_LOW:
        return "inward"
    return "balanced"


def assess_contrast(profile: dict) -> dict:
    """사주 태그를 outward / inward 해석 렌즈에 비추어 요약한다.

    ⚠️ 측정이 아니라 해석 장치다(모듈 docstring 참조). 진단·검사·예측이 아니다.

    Returns:
      label: "outward" | "inward" | "balanced"
      out_score / in_score: 합산 점수(해석용 지표, 성격 점수 아님)
      out_share: out / (out + in)
      signals: 점수에 반영된 신호 목록 [{id, direction, weight}]
      hour_signals_excluded: 시각 미상으로 시주 의존 신호를 뺐는지
      excluded_signals: 점수에서 제외된 신호 id 목록
    """
    pillars = {
        key: (profile.get("pillars") or {}).get(key) or ""
        for key in ("year_pillar", "month_pillar", "day_pillar", "hour_pillar")
    }
    hour_confidence = profile.get("hour_pillar_confidence") or "exact"
    hour_known = hour_confidence == "exact" and bool(pillars.get("hour_pillar"))

    strength = assess_day_master_strength(pillars)
    verdict = strength.get("verdict")
    dist = analyze_element_distribution(pillars)
    sinsal = detect_sinsal(pillars)
    relations = detect_relations(pillars)
    rel_summary = summarize_relations(relations)
    gyeokguk = determine_gyeokguk(pillars).get("name", "")
    yongsin = derive_useful_god(pillars)

    dominant = set(dist.get("dominant") or [])
    deficient = set(dist.get("deficient") or [])

    fired = []
    excluded = []

    # ---- 신강/신약 (대칭) ----
    if verdict == "신강":
        fired.append("S1_STRONG_DAY_MASTER")
    elif verdict == "신약":
        fired.append("N2_WEAK_DAY_MASTER")

    # ---- 신살 (시지 단독 hit 은 시각 미상 시 사라지므로 제외 대상) ----
    if sinsal.get("역마"):
        (excluded if _only_hour_position(sinsal.get("역마")) else fired).append("S2_YEOKMA")
    if sinsal.get("화개"):
        (excluded if _only_hour_position(sinsal.get("화개")) else fired).append("N1_HWAGAE")
    if sinsal.get("괴강"):
        fired.append("S6_GWEGANG")
    if sinsal.get("양인"):
        fired.append("S7_YANGIN")

    # ---- 관계: 일지 충 / 충 존재 / 일지 합 ----
    if rel_summary.get("day_chong"):
        fired.append("S3_DAY_CHONG")
    if rel_summary.get("has_chong"):
        chong_positions = {
            p for c in (relations.get("chong") or []) for p in (c.get("positions") or [])
        }
        if chong_positions and chong_positions <= {"hour_pillar"}:
            excluded.append("S4_HAS_CHONG")
        else:
            fired.append("S4_HAS_CHONG")
    if rel_summary.get("day_he"):
        fired.append("N7_DAY_HE")

    # ---- 격국 ----
    if gyeokguk == "상관격":
        fired.append("S8_SANGGWAN")
    elif gyeokguk == "편관격":
        fired.append("S9_PYEONGWAN")
    elif gyeokguk == "정관격":
        fired.append("N6_JEONGGWAN")

    # ---- work_mode ----
    if profile.get("work_mode") == "THE_CHALLENGER":
        fired.append("S12_CHALLENGER")

    # ---- 오행 분포 ----
    if "火" in dominant:
        fired.append("S13_FIRE_DOMINANT")
    if "木" in dominant:
        fired.append("S14_WOOD_DOMINANT")
    if "土" in deficient:
        fired.append("S15_EARTH_DEFICIENT")
    if "火" in deficient:
        fired.append("N3_FIRE_DEFICIENT")
    if "金" in deficient:
        fired.append("N4_METAL_DEFICIENT")
    if "水" in deficient:
        fired.append("N5_WATER_DEFICIENT")

    # ---- 용신 = 식상(신강 조건) ----
    if verdict == "신강" and yongsin.get("yongsin_role") == "식상":
        fired.append("S16_YONGSIN_EXPRESS")

    # ---- 시각 미상: 시주 의존 신호는 '감쇠'가 아니라 '제외' ----
    if hour_known:
        kept = list(fired)
    else:
        kept = []
        for sid in fired:
            if SIGNAL_WEIGHTS[sid][1]:
                excluded.append(sid)
            else:
                kept.append(sid)

    out_score, in_score = _sum_with_decay(kept)
    total = out_score + in_score

    signals = [
        {
            "id": sid,
            "direction": "outward" if sid.startswith("S") else "inward",
            "weight": SIGNAL_WEIGHTS[sid][0],
        }
        for sid in kept
    ]

    return {
        "label": label_for(out_score, in_score),
        "out_score": out_score,
        "in_score": in_score,
        "out_share": round((out_score / total) if total else 0.0, 3),
        "signals": signals,
        "hour_signals_excluded": bool(excluded) and not hour_known,
        "excluded_signals": sorted(set(excluded)),
    }

