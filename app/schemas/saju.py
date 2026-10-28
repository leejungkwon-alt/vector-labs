# app/schemas/saju.py
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# SAJU-PATCH:lang-schema
SUPPORTED_LANGS = ("en", "ko", "ja", "zh_cn", "es")


class SajuRequest(BaseModel):
    lang: str = "ko"

    model_config = ConfigDict(extra="forbid")

    birth_date: str = Field(
        ..., examples=["1990-05-05"], description="생년월일 (YYYY-MM-DD)"
    )
    birth_time: Optional[str] = Field(
        default=None,
        examples=["14:30:00"],
        description="출생 시간 (HH:MM:SS 또는 HH:MM). birth_time_mode='exact'일 때만 사용.",
    )
    birth_time_mode: str = Field(
        default="exact",
        examples=["exact", "noon", "day_only"],
        description="exact=정확한 시각(기본), noon=정오 가정, day_only=일주만.",
    )
    timezone_str: str = Field(
        default="Asia/Seoul", examples=["Asia/Seoul"], description="IANA 타임존"
    )
    longitude: float = Field(
        default=126.9780, examples=[126.9780], description="출생지 경도 (기본 서울)"
    )
    correction_mode: str = Field(
        default="lmt", examples=["lmt"], description="시간 보정 모드 (lmt, none)"
    )
    jasi_boundary: int = Field(
        default=23, examples=[23], description="자시 경계 (23 또는 0)"
    )
    gender: str = Field(default="M", examples=["M"], description="성별 (M 또는 F)")
    target_year: Optional[int] = Field(
        default=None, examples=[2026], description="운세 조회 대상 절기년 (입춘~입춘). 올해의 흐름/이번 달의 흐름."
    )
    use_current_solar_year: bool = Field(
        default=False,
        description=(
            "true면 요청 시점(now) 기준 절기년(입춘 기준)을 자동 계산하여 "
            "year/monthly 섹션을 채운다. target_year와 동시 지정 불가."
        ),
    )
    birth_location: Optional[str] = Field(
        default=None,
        examples=["seoul", "new_york", "tokyo"],
        description="도시 프리셋 키. 지정 시 longitude/timezone_str보다 우선. "
                    "목록은 list_cities()로 확인.",
    )
    dst_fold: Optional[int] = Field(
        default=None,
        examples=[0, 1],
        description="DST 중복 시각 선택 (0=첫 번째, 1=두 번째). 모호하지 않으면 무시.",
    )

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: str) -> str:
        try:
            dt = datetime.strptime(v, "%Y-%m-%d")
            if not (1900 <= dt.year <= 2100):
                raise ValueError("연도는 1900년에서 2100년 사이여야 합니다.")
        except ValueError as e:
            if "연도는" in str(e):
                raise e
            raise ValueError("birth_date must be in YYYY-MM-DD format")
        return dt.strftime("%Y-%m-%d")  # 1990-5-5 -> 1990-05-05 정규화

    @field_validator("birth_time")
    @classmethod
    def validate_birth_time(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                dt = datetime.strptime(v, fmt)
                return dt.strftime("%H:%M:%S")
            except ValueError:
                continue
        raise ValueError("birth_time must be in HH:MM:SS or HH:MM format")

    @field_validator("birth_time_mode")
    @classmethod
    def validate_birth_time_mode(cls, v: str) -> str:
        if v not in ("exact", "noon", "day_only"):
            raise ValueError(
                "birth_time_mode must be 'exact', 'noon', or 'day_only'."
            )
        return v

    @model_validator(mode="after")
    def validate_birth_time_combination(self):
        mode = self.birth_time_mode
        bt = self.birth_time
        if mode == "exact" and bt is None:
            raise ValueError(
                "birth_time is required when birth_time_mode='exact'."
            )
        if mode != "exact" and bt is not None:
            raise ValueError(
                f"birth_time must be omitted when birth_time_mode='{mode}'."
            )
        return self

    @model_validator(mode="after")
    def validate_year_mode(self):
        if self.target_year is not None and self.use_current_solar_year:
            raise ValueError(
                "target_year and use_current_solar_year are mutually exclusive."
            )
        return self

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        if not (-180.0 <= v <= 180.0):
            raise ValueError("Longitude must be between -180 and 180 degrees.")
        return v

    @field_validator("jasi_boundary")
    @classmethod
    def validate_jasi_boundary(cls, v: int) -> int:
        if v not in (23, 0):
            raise ValueError("jasi_boundary must be 23 or 0.")
        return v

    @field_validator("correction_mode")
    @classmethod
    def validate_correction_mode(cls, v: str) -> str:
        mode = v.lower()
        if mode not in ("lmt", "none"):
            raise ValueError("correction_mode must be 'lmt' or 'none'.")
        return mode

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        g = v.upper()
        if g not in ("M", "F", "남", "여"):
            raise ValueError("gender must be 'M' or 'F'.")
        return "M" if g in ("M", "남") else "F"

    @field_validator("target_year")
    @classmethod
    def validate_target_year(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not (1900 <= v <= 2100):
            raise ValueError("target_year는 1900년에서 2100년 사이여야 합니다.")
        return v

    @field_validator("dst_fold")
    @classmethod
    def validate_dst_fold(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v not in (0, 1):
            raise ValueError("dst_fold must be 0 or 1")
        return v


class SajuResponse(BaseModel):
    solar_year: int
    year_pillar: str
    month_pillar: str
    day_pillar: str
    hour_pillar: Optional[str] = None
    hour_pillar_confidence: Optional[str] = None
    birth_time_mode: Optional[str] = None
    solar_adjusted_time: str
    birth_instant_utc: str
    daewoon_info: Optional[Dict[str, Any]] = None
    ten_gods: Optional[Dict[str, Optional[Dict[str, Any]]]] = None
    luck_info: Optional[Dict[str, Any]] = None
    # ---- Step 9-A 신규 ----
    birth_date: Optional[str] = None
    birth_location: Optional[str] = None
    region: Optional[str] = None


class ReportRequest(SajuRequest):
    """완성 리포트 요청. SajuRequest의 모든 필드 + lang."""
    lang: str = Field(default="en", examples=["en", "ko"], description="리포트 언어")

    @field_validator("lang")
    @classmethod
    def validate_lang(cls, v: str) -> str:
        if v not in SUPPORTED_LANGS:
            raise ValueError(f"lang must be one of {SUPPORTED_LANGS}")
        return v


class ReportResponse(BaseModel):
    report: Dict[str, Any]