# tests/test_premium_content.py
"""
프리미엄 심화 콘텐츠 (love, career, wealth) 테스트
- 콘텐츠 로딩 및 조립 검증
- 티어별 게이팅(잠금) 로직 검증
"""
import pytest
from app.engine.calculator import calculate_saju
from app.semantic.tagger import build_semantic_profile
from app.services.content_writer import (
    generate_full_report,
    write_love_section,
    write_career_section,
    write_wealth_section,
)
from app.services.entitlements import apply_entitlement_gate


def _profile(lang="ko"):
    """테스트용 기본 프로필 (1974년생 남성, THE_RADIATOR)"""
    result = calculate_saju(
        birth_date="1974-02-24",
        birth_time="05:30:00",
        birth_location="seoul",
        correction_mode="lmt",
        jasi_boundary=23,
        gender="M",
        target_year=2026,
    )
    return build_semantic_profile(result)


# ============================================================
# 1. 콘텐츠 로딩 및 조립 테스트
# ============================================================

def test_premium_sections_in_full_report():
    """generate_full_report에 3개 심화 섹션이 포함되어야 함."""
    profile = _profile()
    report = generate_full_report(profile, lang="ko")
    sections = report["sections"]

    assert "love" in sections
    assert "career" in sections
    assert "wealth" in sections

    # 각 섹션의 기본 구조 검증
    for sid in ("love", "career", "wealth"):
        sec = sections[sid]
        assert sec["id"] == sid
        assert sec["mode"] == "THE_RADIATOR"  # 1974년생은 태양(丙) 일간
        assert sec["headline"]
        assert sec["body"]
        assert len(sec["actions"]) > 0
        assert len(sec["patterns"]) > 0
        assert sec["compatibility"]["best_match"]


def test_premium_section_ko_content():
    """한국어 팩이 제대로 로드되는지 검증."""
    profile = _profile()
    love_sec = write_love_section(profile, lang="ko")
    assert love_sec["title"] == "연애와 결혼"
    assert any("\uac00" <= ch <= "\ud7a3" for ch in love_sec["headline"])


def test_premium_section_en_content():
    """영어 팩이 제대로 로드되는지 검증 — 실제 콘텐츠(스텁 아님, 한국어 아님)."""
    profile = _profile()
    career_sec = write_career_section(profile, lang="en")
    assert career_sec["title"] == "Career & Transition"
    # 실제 EN 콘텐츠가 로드되어야 함
    assert career_sec["headline"]
    assert career_sec["headline"] == (
        "You shine on stage — in sales, marketing, and presentations."
    )
    # 한국어가 새어나오면 실패 (팩 로딩 오류 방지)
    assert not any("\uac00" <= ch <= "\ud7a3" for ch in career_sec["headline"])


# ============================================================
# 2. 티어별 게이팅(Gating) 테스트
# ============================================================

def test_free_tier_locks_premium_sections():
    """무료(free) 티어는 심화 섹션의 본문(body)과 세부 내용이 잠겨야 함."""
    profile = _profile()
    report = generate_full_report(profile, lang="ko")
    
    # free 티어로 게이팅 적용
    gated_report = apply_entitlement_gate(report, tier="free")
    
    for sid in ("love", "career", "wealth"):
        sec = gated_report["sections"][sid]
        
        # keep 필드는 유지
        assert "id" in sec
        assert "title" in sec
        assert "headline" in sec
        
        # 잠금 필드는 제거
        assert "body" not in sec
        assert "actions" not in sec
        assert "patterns" not in sec
        assert "compatibility" not in sec
        assert "red_flags" not in sec
        
        # locked_fields 명시 확인
        assert "body" in sec.get("locked_fields", [])
        assert "actions" in sec.get("locked_fields", [])


def test_premium_tier_unlocks_premium_sections():
    """프리미엄(premium) 티어는 심화 섹션의 본문이 모두 열려야 함."""
    profile = _profile()
    report = generate_full_report(profile, lang="ko")
    
    # premium 티어로 게이팅 적용
    gated_report = apply_entitlement_gate(report, tier="premium")
    
    for sid in ("love", "career", "wealth"):
        sec = gated_report["sections"][sid]
        
        # 모든 필드 유지
        assert "id" in sec
        assert "title" in sec
        assert "headline" in sec
        assert "body" in sec
        assert "actions" in sec
        assert "patterns" in sec
        
        # locked_fields 자체가 없어야 함
        assert "locked_fields" not in sec
