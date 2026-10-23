# app/engine/yongsin.py
"""
나에게 힘이 되는 기운(用神)·나를 도와주는 기운(喜神)·조심해야 할 기운(忌神) 도출.

억부나에게 힘이 되는 기운 (抑扶用神) 기본:
  신강 → 일간을 洩(식상)·耗(재성)·剋(관성)하는 오행이 나에게 힘이 되는 기운
  신약 → 일간을 生(인성)·助(비겁)하는 오행이 나에게 힘이 되는 기운
  중화 → 조후(調候)로 보정

조후법 (調候法) — 계절 기후 균형:
  여름(巳午未) → 水로 식힘
  겨울(亥子丑) → 火로 따뜻하게
  봄·가을 → 계절 중간, support ratio 방향으로 약하게
"""
from app.engine.elements import STEM_TO_ELEMENT, ELEMENT_NAMES
from app.engine.strength import assess_day_master_strength


_SUMMER_MONTHS = {"巳", "午", "未"}
_WINTER_MONTHS = {"亥", "子", "丑"}


def _role_elements(day_elem: str) -> dict:
    """
    일간 오행 기준 각 십성 역할의 오행.

    일간 火(idx=1) 기준:
      비겁 = 火(1)
      인성 = 木(0)   ← 木生火
      식상 = 土(2)   ← 火生土
      재성 = 金(3)   ← 火剋金
      관성 = 水(4)   ← 水剋火
    """
    dm_idx = ELEMENT_NAMES.index(day_elem)
    return {
        "비겁": ELEMENT_NAMES[dm_idx],
        "인성": ELEMENT_NAMES[(dm_idx - 1) % 5],
        "식상": ELEMENT_NAMES[(dm_idx + 1) % 5],
        "재성": ELEMENT_NAMES[(dm_idx + 2) % 5],
        "관성": ELEMENT_NAMES[(dm_idx + 3) % 5],
    }


def derive_useful_god(pillars: dict) -> dict:
    """
    억부 + 조후 결합 나에게 힘이 되는 기운 도출.

    반환:
      yongsin:        주 나에게 힘이 되는 기운 오행
      yongsin_role:   나에게 힘이 되는 기운의 십성 역할 (인성/비겁/식상/재성/관성/조후)
      huisin:         나를 도와주는 기운 오행
      huisin_role:    나를 도와주는 기운의 십성 역할
      gisin:          조심해야 할 기운 오행 리스트
      gisin_roles:    조심해야 할 기운 십성 역할 리스트
      reason:         판정 근거 (디버깅·콘텐츠 노출용)
      strength:       원본 신강/신약 판정 결과
      role_map:       역할→오행 매핑 (콘텐츠/디버깅 활용)
    """
    day_stem = pillars["day_pillar"][0]
    day_elem = STEM_TO_ELEMENT[day_stem]
    roles = _role_elements(day_elem)
    role_to_elem = {v: k for k, v in roles.items()}

    strength = assess_day_master_strength(pillars)
    verdict = strength["verdict"]
    ratio = strength["support_ratio"]
    month_branch = pillars["month_pillar"][1]

    # 오행을 직접 지정하는 조후 케이스와, 역할 이름으로 지정하는 억부 케이스 분리
    yongsin_source = "억부"
    if verdict == "신강":
        if ratio >= 0.75:
            yongsin_role = "관성"
            huisin_role = "재성"
            gisin_roles = ["인성", "비겁"]
            reason = f"신강 (ratio={ratio}) → 관성으로 제압"
        else:
            yongsin_role = "식상"
            huisin_role = "재성"
            gisin_roles = ["인성", "비겁"]
            reason = f"신강 (ratio={ratio}) → 식상으로 설기"

        yongsin = roles[yongsin_role]
        huisin = roles[huisin_role]
        gisin = [roles[r] for r in gisin_roles]

    elif verdict == "신약":
        yongsin_role = "인성"
        huisin_role = "비겁"
        gisin_roles = ["재성", "관성", "식상"]
        reason = f"신약 (ratio={ratio}) → 인성으로 생조"

        yongsin = roles[yongsin_role]
        huisin = roles[huisin_role]
        gisin = [roles[r] for r in gisin_roles]

    else:  # 중화
        yongsin_source = "조후"
        if month_branch in _SUMMER_MONTHS:
            yongsin = "水"
            huisin = "金"
            gisin = ["火", "木", "土"]
            reason = f"중화 (ratio={ratio}) + 여름생 → 水로 조후"
        elif month_branch in _WINTER_MONTHS:
            yongsin = "火"
            huisin = "木"
            gisin = ["水", "金", "土"]
            reason = f"중화 (ratio={ratio}) + 겨울생 → 火로 조후"
        else:
            # 계절 중간: support ratio 방향으로 약하게
            if ratio >= 0.5:
                yongsin_role = "식상"
                huisin_role = "재성"
                gisin_roles = ["인성", "비겁"]
            else:
                yongsin_role = "인성"
                huisin_role = "비겁"
                gisin_roles = ["재성", "관성", "식상"]

            yongsin = roles[yongsin_role]
            huisin = roles[huisin_role]
            gisin = [roles[r] for r in gisin_roles]
            reason = f"중화 (ratio={ratio}), 계절 중간 → {yongsin_role} 위주"

    # 역할 라벨 최종 확정
    yongsin_role = role_to_elem.get(yongsin, "조후") if yongsin_source == "억부" else "조후"
    huisin_role = role_to_elem.get(huisin, "조후")
    gisin_roles = [role_to_elem.get(e, "조후") for e in gisin]

    return {
        "yongsin": yongsin,
        "yongsin_role": yongsin_role,
        "huisin": huisin,
        "huisin_role": huisin_role,
        "gisin": gisin,
        "gisin_roles": gisin_roles,
        "reason": reason,
        "yongsin_source": yongsin_source,
        "strength": strength,
        "role_map": roles,
    }