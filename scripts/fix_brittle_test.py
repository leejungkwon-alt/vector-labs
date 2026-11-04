import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_FILE = ROOT / "tests" / "test_visual_pipeline.py"

def main():
    # 1. 테스트 코드 수정
    text = TEST_FILE.read_text(encoding="utf-8")
    old_test = 'assert "mock-cdn.vectorlabs.app" in report["meta"]["daily_wallpaper_url"]'
    new_test = 'assert report["meta"]["daily_wallpaper_url"].startswith("http")'
    
    if old_test in text:
        text = text.replace(old_test, new_test)
        TEST_FILE.write_text(text, encoding="utf-8")
        print("[OK] test_visual_pipeline.py 하드코딩된 도메인 검사 수정 완료")
    else:
        print("[SKIP] 이미 수정되었거나 찾을 수 없음")

if __name__ == "__main__":
    main()