# app/api/v1/endpoints/saju.py
from fastapi import APIRouter, Depends, HTTPException

from app.engine.calculator import calculate_saju
from app.schemas.saju import (
    InterpretRequest,
    InterpretResponse,
    SajuRequest,
    SajuResponse,
)
from app.services.template_interpreter import generate_template_interpretation
from app.auth.dependencies import get_current_user_optional

import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter()


def _require_auth_interpret() -> bool:
    v = os.environ.get("SAJU_REQUIRE_AUTH_FOR_INTERPRET", "").lower()
    return v in ("1", "true", "yes", "on")


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
            target_year=payload.target_year,
            dst_fold=payload.dst_fold, 
            birth_location=payload.birth_location, 
        )
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Unexpected error during calculate_saju")
        raise HTTPException(
            status_code=500, detail="Internal server error during calculation."
        )


@router.post("/interpret", response_model=InterpretResponse)
def api_interpret_saju(
    payload: InterpretRequest,
    current_user: dict | None = Depends(get_current_user_optional),
):
    """계산된 사주 데이터를 바탕으로 템플릿 기반 해석 리포트를 생성합니다."""
    if _require_auth_interpret() and current_user is None:
        raise HTTPException(status_code=401, detail="Authentication required.")
    try:
        interpretation = generate_template_interpretation(
            payload.saju_data.model_dump(), lang=payload.lang
        )
        return {"interpretation": interpretation}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Unexpected error during template interpretation")
        raise HTTPException(status_code=500, detail="Template interpretation failed.")