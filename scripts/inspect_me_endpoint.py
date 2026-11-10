import glob
import re

print("🔎 /me 엔드포인트와 _one 메서드를 검색합니다...\n")

for filepath in glob.glob("app/**/*.py", recursive=True):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
        # 1. /me 엔드포인트 찾기
        if '"/me"' in content or "'/me'" in content or '"/auth/me"' in content:
            print(f"===== [엔드포인트 발견] {filepath} =====")
            match = re.search(r"(@router\.get\([\'\"].*/me[\'\"].*\n(?:.*\n)*?)(?=\n@router|\Z)", content)
            if match:
                print(match.group(1).strip())
            else:
                # 정규식 매칭 실패 시 해당 파일의 라인 출력
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if '/me' in line:
                        print('\n'.join(lines[max(0, i-2):min(len(lines), i+20)]))
                        break
            print("-" * 60)
        
        # 2. _one 메서드 찾기
        if "def _one(" in content:
            print(f"===== [_one 메서드 발견] {filepath} =====")
            match = re.search(r"(def _one\(.*\n(?:.*\n)*?)(?=\ndef |\n@|\Z)", content)
            if match:
                print(match.group(1).strip())
            print("-" * 60)

print("\n✨ 위에 출력된 코드를 복사해서 저에게 보여주세요!")