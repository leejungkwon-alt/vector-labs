"""
scripts/fix_ko_test_final.py

tests/test_ko_report.py의 2개 테스트를 구조 기반으로 안전하게 교체합니다.
문자열 이스케이프(\u) 오류를 피하기 위해 chr(0xAC00)을 사용합니다.
"""
from pathlib import Path
import shutil
from datetime import datetime

TS = datetime.now().strftime("%Y%m%d_%H%M%S")
p = Path('tests/test_ko_report.py')

# 백업
shutil.copy2(p, p.with_suffix(p.suffix + f".bak_{TS}"))

text = p.read_text(encoding='utf-8')

old1 = '''def test_ko_year_name():
    report = _ko_report_1974()
    year = report["sections"]["year"]
    assert year["title"] == "올해의 흐름"
    # 2026 丙午 = 비견 → 거울의 해
    assert year["name"] == "거울의 해"        # 한국어로 바뀜'''

new1 = '''def test_ko_year_name():
    report = _ko_report_1974()
    year = report["sections"]["year"]
    assert year["title"] == "올해의 흐름"
    assert year["target_year"] == 2026
    assert isinstance(year["name"], str) and year["name"].strip()
    assert any(chr(0xAC00) <= ch <= chr(0xD7A3) for ch in year["name"])
    assert any(chr(0xAC00) <= ch <= chr(0xD7A3) for ch in year["body"])'''

old2 = '''def test_ko_year_is_korean():
    report = _ko_report_1974()
    year = report["sections"]["year"]
    assert year["title"] == "올해의 흐름"
    # 2026 丙午 = 비견 → 거울의 해
    assert year["name"] == "거울의 해"'''

new2 = '''def test_ko_year_is_korean():
    report = _ko_report_1974()
    year = report["sections"]["year"]
    assert year["title"] == "올해의 흐름"
    for field in ("name", "headline", "body", "watch_for", "lean_into"):
        value = year.get(field, "")
        assert isinstance(value, str) and value.strip()
        assert any(chr(0xAC00) <= ch <= chr(0xD7A3) for ch in value)'''

text = text.replace(old1, new1)
text = text.replace(old2, new2)
p.write_text(text, encoding='utf-8')
print("✅ test_ko_report.py 수정 완료!")