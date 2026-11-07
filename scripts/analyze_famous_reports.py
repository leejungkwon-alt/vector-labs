# scripts/analyze_famous_reports.py
"""
저장된 유명인 사주 JSON을 읽어서, 사주 기둥(년월일시)과 대운(10년 주기)을 요약 출력.
"""
import json
from pathlib import Path

REPORT_DIR = Path("scripts/famous_reports")

if not REPORT_DIR.exists():
    print(f"❌ {REPORT_DIR} 폴더가 없습니다. 먼저 validate_famous.py를 실행하세요.")
    exit()

files = list(REPORT_DIR.glob("*.json"))
if not files:
    print("❌ 저장된 JSON 파일이 없습니다.")
    exit()

for f in files:
    if "error" in f.name:
        continue
        
    with open(f, "r", encoding="utf-8") as fp:
        data = json.load(fp)
        
    person = data.get("person", {})
    res = data.get("saju_result", {})
    
    name = person.get("name", "Unknown")
    known_for = person.get("known_for", "?")
    birth_date = person.get("birth_date", "?")
    
    # 기본 기둥
    yp = res.get("year_pillar", "?")
    mp = res.get("month_pillar", "?")
    dp = res.get("day_pillar", "?")
    hp = res.get("hour_pillar", "?")
    
    # 대운 정보
    dw = res.get("daewoon_info") or {}
    dw_pillars = dw.get("daewoon_pillars", [])
    
    print("=" * 60)
    print(f"👤 {name} ({birth_date})")
    print(f"   생전 주요 업적: {known_for}")
    print("-" * 60)
    print(f"🔮 사주 (四柱)")
    print(f"   년주: {yp} | 월주: {mp} | 일주(본질): {dp} | 시주: {hp}")
    print(f"   (일간/일주가 '나'의 핵심 기운입니다)")
    
    if dw_pillars:
        print("-" * 60)
        print(f"🔄 대운 흐름 (10년 주기)")
        for p in dw_pillars:
            start = p.get("start_age")
            end = p.get("end_age")
            pillar = p.get("pillar")
            # 너무 먼 미래는 생략
            if start > 80:
                continue
            print(f"   {start:>2}세 ~ {end:>2}세 : {pillar}")
    print("\n")

print("=" * 60)
print("💡 [분석 가이드]")
print("1. '일주(day_pillar)'의 첫 글자(일간)가 그 사람의 본질입니다.")
print("2. 예: Steve Jobs의 일주는 '丙辰' -> '丙(병화)'는 태양, 열정, 혁신, 리더십을 의미합니다.")
print("3. 대운의 흐름과 실제 인생의 굴곡(창업, 실패, 전성기)을 비교해 보세요.")