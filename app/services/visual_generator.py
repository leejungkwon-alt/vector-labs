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

def get_daily_wallpaper_url(profile: dict) -> str:
    """
    유저의 프로필을 받아 매핑된 3D 아트워크 이미지 URL을 반환합니다.
    """
    # 1. 주 오행 추출 (없으면 FLOW 기본값)
    dominant = profile.get("energy_signature", {}).get("dominant", [])
    elem_sig = dominant[0] if dominant else "FLOW"
    elem_str = ELEMENT_MAP.get(elem_sig, "water")

    # 2. 주 행동 모드 추출 (없으면 THE_GENERALIST 기본값)
    work_mode = profile.get("work_mode", "THE_GENERALIST")
    mode_str = "generalist"  # 임시: 5장 테스트를 위해 고정

    # 3. 파일명 조합 (예: bg_wood_creator.webp)
    filename = f"bg_{elem_str}_{mode_str}.webp"

    # 4. CDN/Supabase URL 반환 (환경변수로 설정 가능)
    base_url = os.environ.get("SAJU_ASSET_BASE_URL", "https://mock-cdn.vectorlabs.app/wallpapers/")
    if not base_url.endswith("/"):
        base_url += "/"
    
    return urljoin(base_url, filename)
