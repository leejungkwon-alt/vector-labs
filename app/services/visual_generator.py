"""
app/services/visual_generator.py

유저의 사주 프로필을 기반으로 3D 아트워크 배경화면 URL을 생성합니다.
- 오행(Dominant Element) + 십성(Work Mode) 조합
"""
import os
from urllib.parse import urljoin

# 오행 시그니처 -> 파일명 접두어
ELEMENT_MAP = {
    "GROWTH": "wood",
    "SPARK": "fire",
    "GROUND": "earth",
    "EDGE": "metal",
    "FLOW": "water"
}

# 십성 모드 -> 파일명 접미어
MODE_MAP = {
    "THE_CREATOR": "creator",
    "THE_CHALLENGER": "challenger",
    "THE_OFFICER": "officer",
    "THE_SURVIVOR": "survivor",
    "THE_MYSTIC": "mystic",
    "THE_MENTOR": "mentor",
    "THE_GENERALIST": "generalist",
    "THE_STEWARD": "steward",
    "THE_OPERATOR": "operator",
    "THE_FLOW": "flow"
}

def _resolve_asset_base_url() -> str:
    """
    SAJU_ASSET_BASE_URL 우선, 개발/테스트에서는 mock-cdn 폴백.
    production 에서 미설정 시 RuntimeError (silent 404 이미지 방지).

    SAJU_JWT_SECRET / SAJU_DATABASE_URL 과 동일한 lazy fail 패턴을 따른다.
    """
    base_url = os.environ.get("SAJU_ASSET_BASE_URL", "").strip()
    is_prod = os.environ.get("SAJU_ENV", "").lower() == "production"

    if not base_url:
        if is_prod:
            raise RuntimeError(
                "SAJU_ASSET_BASE_URL must be set in production. "
                "Report meta includes a daily wallpaper URL; without a real "
                "CDN every user would receive a 404 image."
            )
        base_url = "https://mock-cdn.vectorlabs.app/wallpapers/"
    if not base_url.endswith("/"):
        base_url += "/"
    return base_url


def get_daily_wallpaper_url(profile: dict) -> str:
    """
    유저의 프로필을 받아 매핑된 3D 아트워크 이미지 URL을 반환합니다.
    production 에서 SAJU_ASSET_BASE_URL 미설정 시 RuntimeError.
    """
    dominant = profile.get("energy_signature", {}).get("dominant", [])
    elem_sig = dominant[0] if dominant else "FLOW"
    elem_str = ELEMENT_MAP.get(elem_sig, "water")

    work_mode = profile.get("work_mode", "THE_GENERALIST")
    mode_str = MODE_MAP.get(work_mode, "generalist")

    filename = f"bg_{elem_str}_{mode_str}.webp"

    return urljoin(_resolve_asset_base_url(), filename)
