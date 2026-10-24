#!/usr/bin/env python3
"""
scripts/refactor_plain_language.py
사용자에게 노출되는 데이터를 '쉬운 언어(Plain Language)'로 정제합니다.
- 한자 기둥명(pillar) 노출 방지 및 제거
- 어려운 영어 코드(TEN_GOD_*, THE_*) 및 사주 용어 최소화
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
CW = ROOT / "app" / "services" / "content_writer.py"

def main():
    if not CW.exists():
        print("❌ content_writer.py를 찾을 수 없습니다.")
        return

    src = CW.read_text(encoding="utf-8")
    original_src = src

    # 1. write_year_section: 한자(pillar) 대신 쉬운 이름(pillar_name)만 내려주기
    src = src.replace(
        '        "pillar": year_theme.get("pillar"),',
        '        "pillar": None,  # 평이화: 한자 기둥명 노출 방지'
    )
    
    # 2. write_monthly_section: items.append 내부 수정
    src = re.sub(
        r'"pillar":\s*m\["pillar"\],',
        '"pillar": None,  # 평이화: 한자 노출 방지',
        src
    )
    
    # 3. write_timeline_section: items.append 내부 수정
    src = re.sub(
        r'"pillar":\s*d\["pillar"\],',
        '"pillar": None,  # 평이화: 한자 노출 방지',
        src
    )

    # 4. 연운(Year) 및 월운(Monthly)의 어려운 영어 코드(ten_god) 노출 제거
    # 기존 템플릿에서 영어 코드가 그대로 노출되지 않도록, 프론트엔드에서 안 쓰도록 None 처리하거나
    # 사용자용 한글 라벨을 별도로 넘겨주도록 구조 변경
    src = src.replace(
        '        "ten_god": ten_god,',
        '        "ten_god": None,  # 평이화: 영어 코드 숨김'
    )

    if src != original_src:
        # 백업 생성
        bak = CW.with_suffix(CW.suffix + ".bak.plain")
        bak.write_text(original_src, encoding="utf-8")
        
        CW.write_text(src, encoding="utf-8")
        print("✅ content_writer.py 평이화 패치 완료! (백업: content_writer.py.bak.plain)")
    else:
        print("⚠️ 이미 패치되었거나 대상 코드를 찾을 수 없습니다.")

if __name__ == "__main__":
    main()