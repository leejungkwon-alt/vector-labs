import re
from pathlib import Path

print("🚀 2단계: 테스트 수정 및 코드 청소 시작...\n")

# ---------------------------------------------------------
# [테스트 수정] test_visual_pipeline.py (하드코딩된 기대값 변경)
# ---------------------------------------------------------
test_visual = Path("tests/test_visual_pipeline.py")
if test_visual.exists():
    code = test_visual.read_text(encoding="utf-8")
    # generalist -> mystic (프로필의 work_mode에 맞게 수정)
    code = code.replace(
        'assert "bg_wood_generalist.webp" in url',
        'assert "bg_wood_mystic.webp" in url'
    )
    test_visual.write_text(code, encoding="utf-8")
    print("✅ 테스트 수정 완료: test_visual_pipeline.py")

# ---------------------------------------------------------
# [9번] content_writer.py 코드 청소
# ---------------------------------------------------------
writer = Path("app/services/content_writer.py")
if writer.exists():
    code = writer.read_text(encoding="utf-8")
    original = code
    
    # 1. EASY_DAEWOON 데드코드 제거
    code = re.sub(r"EASY_DAEWOON = \{.*?\}\n\n", "", code, flags=re.DOTALL)
    
    # 2. 전역 PILLAR_KO_MAP 제거 (내부 _translate_pillar의 PILLAR_MAP과 중복)
    code = re.sub(r"# --- 실시간 한자 번역기 추가 ---\nPILLAR_KO_MAP = \{.*?\}\n\n", "", code, flags=re.DOTALL)
    
    # 3. PILLAR_KO_MAP 호출부를 _translate_pillar 호출로 교체
    code = code.replace("PILLAR_KO_MAP.get(", "_translate_pillar(")
    # _translate_pillar는 두 개의 인자를 받으므로, 기존 2번째 인자(기본값) 제거
    # 패턴: _translate_pillar(current_dw["pillar"], current_dw["pillar"]) -> _translate_pillar(current_dw["pillar"])
    code = re.sub(r'_translate_pillar\(([^,]+), [^)]+\)', r'_translate_pillar(\1)', code)
    
    # 4. 미사용 import 제거 (from datetime import date as _date)
    code = code.replace("from datetime import date as _date\n", "")
    
    # 5. 개발자 잔재 주석 제거
    code = code.replace("    # 이 부분을 찾아서 아래처럼 수정하세요!\n", "")
    code = code.replace("    # 👇 이렇게 수정\n", "")
    
    if code != original:
        writer.write_text(code, encoding="utf-8")
        print("✅ 코드 청소 완료: content_writer.py (데드코드/주석/중복 제거)")
    else:
        print("➖ 변경 사항 없음: content_writer.py")

# ---------------------------------------------------------
# [12번] frontend client.ts 타임아웃 주석 수정 (10초 -> 30초)
# ---------------------------------------------------------
client_ts = Path("frontend/src/api/client.ts")
if client_ts.exists():
    code = client_ts.read_text(encoding="utf-8")
    code = code.replace("// 10초 타임아웃 설정", "// 30초 타임아웃 설정")
    client_ts.write_text(code, encoding="utf-8")
    print("✅ 주석 수정 완료: client.ts (10초 -> 30초)")

print("\n🎉 2단계 작업 완료!")