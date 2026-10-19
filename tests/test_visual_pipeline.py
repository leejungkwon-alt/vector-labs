"""3D 아트워크 매핑 파이프라인 테스트."""
from app.engine.calculator import calculate_saju
from app.semantic.tagger import build_semantic_profile
from app.services.visual_generator import get_daily_wallpaper_url
from app.services.content_writer import generate_full_report


def _profile(birth_date="1974-02-24", birth_time="05:30:00"):
    result = calculate_saju(
        birth_date=birth_date, birth_time=birth_time,
        birth_location="seoul", correction_mode="lmt", jasi_boundary=23, gender="M",
    )
    return build_semantic_profile(result)


def test_wallpaper_url_mapping():
    """오행과 십성에 따라 올바른 파일명이 생성되어야 함."""
    # 1974 케이스: 목(GROWTH) + 탐구자(THE_MYSTIC)
    profile = _profile()
    url = get_daily_wallpaper_url(profile)
    assert "bg_wood_generalist.webp" in url
    
    # 1990 케이스: 금(EDGE) + (work_mode에 따라 다름)
    profile_1990 = _profile("1990-05-05", "14:30:00")
    url_1990 = get_daily_wallpaper_url(profile_1990)
    assert "bg_metal_generalist.webp" in url_1990


def test_report_contains_wallpaper_url():
    """리포트 meta 데이터에 wallpaper_url이 포함되어야 함."""
    profile = _profile()
    report = generate_full_report(profile, lang="en")
    
    assert "daily_wallpaper_url" in report["meta"]
    assert report["meta"]["daily_wallpaper_url"].endswith(".webp")
    assert "mock-cdn.vectorlabs.app" in report["meta"]["daily_wallpaper_url"]
