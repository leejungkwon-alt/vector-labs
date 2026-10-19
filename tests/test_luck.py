from app.engine.luck import calculate_monthly_lucks, calculate_annual_luck

def test_calculate_annual_luck():
    annual = calculate_annual_luck(2026)
    assert annual["year"] == 2026
    assert isinstance(annual["pillar"], str)
    assert len(annual["pillar"]) == 2

def test_calculate_monthly_lucks_boundary():
    """월운 연도 경계값 검증 (자월=당해년도 12월, 축월=다음해 1월)"""
    target_year = 2026
    monthly_lucks = calculate_monthly_lucks(target_year)
    
    assert len(monthly_lucks) == 12
    
    # 11번째 달: 子월 (인덱스 10) -> 2026-12여야 함
    zi_month = monthly_lucks[10]
    assert zi_month["branch"] == "子"
    assert zi_month["approx_solar_month"] == "2026-12"
    
    # 12번째 달: 丑월 (인덱스 11) -> 2027-01여야 함 (다음 해)
    chul_month = monthly_lucks[11]
    assert chul_month["branch"] == "丑"
    assert chul_month["approx_solar_month"] == "2027-01"