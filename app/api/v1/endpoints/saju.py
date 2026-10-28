# app/api/v1/endpoints/saju.py
from fastapi import APIRouter, Depends, HTTPException

from app.engine.calculator import calculate_saju
from app.schemas.saju import (
    SajuRequest,
    SajuResponse,
)
from app.auth.dependencies import get_current_user_optional
from app.api.errors import format_dst_error
from app.engine.time_correction import DSTAmbiguousError, DSTGapError

import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter()


def _require_auth_calculate() -> bool:
    v = os.environ.get("SAJU_REQUIRE_AUTH_FOR_CALCULATE", "").lower()
    return v in ("1", "true", "yes", "on")


@router.post("/calculate", response_model=SajuResponse)
def api_calculate_saju(
    payload: SajuRequest,
    current_user: dict | None = Depends(get_current_user_optional),
):
    """정밀 사주 명식 및 운세 데이터를 계산합니다."""
    if _require_auth_calculate() and current_user is None:
        raise HTTPException(status_code=401, detail="Authentication required.")
    try:
        return calculate_saju(
            birth_date=payload.birth_date,
            birth_time=payload.birth_time,
            birth_time_mode=payload.birth_time_mode,
            timezone_str=payload.timezone_str,
            longitude=payload.longitude,
            correction_mode=payload.correction_mode,
            jasi_boundary=payload.jasi_boundary,
            gender=payload.gender,
            lang=payload.lang,
            target_year=payload.target_year,
            use_current_solar_year=payload.use_current_solar_year,
            dst_fold=payload.dst_fold, 
            birth_location=payload.birth_location, 
        )
    except (DSTAmbiguousError, DSTGapError) as e:
        raise HTTPException(status_code=400, detail=format_dst_error("en", e))
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Unexpected error during calculate_saju")
        raise HTTPException(
            status_code=500, detail="Internal server error during calculation."
        )

