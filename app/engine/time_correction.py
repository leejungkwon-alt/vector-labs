# app/engine/time_correction.py
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class DSTGapError(ValueError):
    """DST로 건너뛴 존재하지 않는 시각. 엔드포인트에서 lang별 재구성."""
    def __init__(self, clock, tz_key):
        self.clock = clock
        self.tz_key = tz_key
        super().__init__(
            f"존재하지 않는 시각입니다: {clock}은 {tz_key}에서 DST로 건너뛴 시각입니다."
        )


class DSTAmbiguousError(ValueError):
    """DST 종료로 두 번 발생하는 모호한 시각. 엔드포인트에서 lang별 재구성."""
    def __init__(self, clock, tz_key, off0, off1):
        self.clock = clock
        self.tz_key = tz_key
        self.off0 = off0
        self.off1 = off1
        super().__init__(
            f"모호한 시각입니다: {clock}은 {tz_key}에서 두 번 발생합니다. "
            f"dst_fold=0(offset {off0}) 또는 dst_fold=1(offset {off1})로 "
            "재요청해 주세요."
        )


def get_zone(timezone_str: str) -> ZoneInfo:
    try:
        return ZoneInfo(timezone_str)
    except (ZoneInfoNotFoundError, ValueError):
        raise ValueError(f"Invalid timezone: {timezone_str}")


def _resolve_wall_clock(clock: datetime, tz: ZoneInfo,
                        dst_fold: int | None = None) -> datetime:
    """
    벽시계 시각 → aware datetime.

    - DST gap(존재하지 않는 시각): ValueError
    - DST 중복(모호한 시각):
        * dst_fold가 None이면 ValueError (사용자가 0/1 선택하도록 유도)
        * dst_fold가 0 또는 1이면 그 fold로 해석
    """
    if dst_fold is not None and dst_fold not in (0, 1):
        raise ValueError("dst_fold must be 0 or 1")

    aware0 = clock.replace(tzinfo=tz, fold=0)

    # gap 검출
    round_trip = aware0.astimezone(timezone.utc).astimezone(tz).replace(tzinfo=None)
    if round_trip != clock:
        raise DSTGapError(clock, tz.key)

    # ambiguity 검출
    aware1 = clock.replace(tzinfo=tz, fold=1)
    is_ambiguous = aware0.utcoffset() != aware1.utcoffset()

    if is_ambiguous and dst_fold is None:
        off0 = aware0.utcoffset()
        off1 = aware1.utcoffset()
        raise DSTAmbiguousError(clock, tz.key, off0, off1)

    return clock.replace(tzinfo=tz, fold=dst_fold or 0)


def calculate_adjusted_times(
    birth_date,
    birth_time,
    timezone_str,
    longitude,
    correction_mode="lmt",
    dst_fold: int | None = None,
):
    if not (-180.0 <= longitude <= 180.0):
        raise ValueError("Longitude must be between -180 and 180 degrees.")

    mode = correction_mode.lower()
    if "eot" in mode:
        raise NotImplementedError(
            "Equation of Time (EoT) correction is not implemented yet."
        )
    if mode not in ("lmt", "none"):
        raise ValueError(f"Unsupported correction_mode: {correction_mode}")

    tz = get_zone(timezone_str)
    clock = datetime.fromisoformat(f"{birth_date}T{birth_time}")
    aware = _resolve_wall_clock(clock, tz, dst_fold=dst_fold)
    utc_instant = aware.astimezone(timezone.utc)

    if mode == "lmt":
        offset = aware.utcoffset() or timedelta(0)
        corrected_local = clock + timedelta(hours=longitude / 15.0) - offset
    else:
        corrected_local = clock

    return utc_instant, corrected_local