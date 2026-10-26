import re
from pathlib import Path

# ---------------------------------------------------------
# 6. loader.py 중복 정의 제거 (JSON 로더만 남기기)
# ---------------------------------------------------------
loader_path = Path("app/services/content/loader.py")
if loader_path.exists():
    code = loader_path.read_text(encoding="utf-8")
    # 맨 끝의 중복된 list_available 함수(REGISTRY 기반) 제거
    # (파일 끝부분에 있는 두 번째 def list_available... 블록을 통째로 날립니다)
    pattern = r"def list_available\(lang: str\) -> list:\s+# 해당 언어에서 사용 가능한 섹션 목록\.\s+return list\(_REGISTRY\.get\(lang, \{\}\)\.keys\(\)\)"
    code = re.sub(pattern, "", code)
    loader_path.write_text(code.strip() + "\n", encoding="utf-8")
    print("✅ 6. loader.py 중복 정의 제거 완료")

# ---------------------------------------------------------
# 7. tagger.py에 birth_date 추가 (비로그인 유저도 변형 콘텐츠 적용)
# ---------------------------------------------------------
tagger_path = Path("app/semantic/tagger.py")
if tagger_path.exists():
    code = tagger_path.read_text(encoding="utf-8")
    # return 딕셔너리에 birth_date 추가
    if '"birth_date": saju_result.get("birth_date"),' not in code:
        code = code.replace(
            '"pillars": pillars,                # ---- C+ ----',
            '"pillars": pillars,                # ---- C+ ----\n        "birth_date": saju_result.get("birth_date"),'
        )
    tagger_path.write_text(code, encoding="utf-8")
    print("✅ 7. tagger.py birth_date 반환 추가 완료")

# ---------------------------------------------------------
# 8. yongsin.py 조후(계절) 로직 버그 수정
# ---------------------------------------------------------
yongsin_path = Path("app/engine/yongsin.py")
if yongsin_path.exists():
    code = yongsin_path.read_text(encoding="utf-8")
    
    # 조후 판별 플래그 추가
    if "yongsin_source" not in code:
        # 중화 로직 부분 수정
        old_logic = '''    else:  # 중화
        if month_branch in _SUMMER_MONTHS:'''
        new_logic = '''    else:  # 중화
        yongsin_source = "조후"
        if month_branch in _SUMMER_MONTHS:'''
        code = code.replace(old_logic, new_logic)
        
        # 신강/신약 로직 부분 수정
        code = code.replace(
            '    if verdict == "신강":',
            '    yongsin_source = "억부"\n    if verdict == "신강":'
        )
        
        # 리턴 딕셔너리에 yongsin_source 추가
        code = code.replace(
            '    # 역할 라벨 최종 확정 (조후 케이스에서 오행 → 역할 역매핑)\n    yongsin_role = role_to_elem.get(yongsin, "조후")',
            '    # 역할 라벨 최종 확정\n    yongsin_role = role_to_elem.get(yongsin, "조후") if yongsin_source == "억부" else "조후"'
        )
        code = code.replace(
            '        "reason": reason,',
            '        "reason": reason,\n        "yongsin_source": yongsin_source,'
        )
    yongsin_path.write_text(code, encoding="utf-8")
    print("✅ 8. yongsin.py 조후 로직 수정 완료")

# ---------------------------------------------------------
# 10. visual_generator.py 하드코딩된 generalist 수정
# ---------------------------------------------------------
visual_path = Path("app/services/visual_generator.py")
if visual_path.exists():
    code = visual_path.read_text(encoding="utf-8")
    code = code.replace(
        '    mode_str = "generalist"  # 임시: 5장 테스트를 위해 고정',
        '    mode_str = MODE_MAP.get(work_mode, "generalist")'
    )
    visual_path.write_text(code, encoding="utf-8")
    print("✅ 10. visual_generator.py work_mode 매핑 복원 완료")

print("\n🎉 1단계 백엔드 핵심 버그 4가지 수정이 완료되었습니다!")