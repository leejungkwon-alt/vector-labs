# scripts/find_403_source.py
from pathlib import Path

print("🔎 백엔드 코드에서 403 반환 위치 및 /saju/daily 관련 파일을 검색합니다...\n")

for p in Path(".").rglob("*.py"):
    if any(x in p.parts for x in ["venv", "__pycache__", "node_modules", ".git"]):
        continue
    try:
        txt = p.read_text(encoding="utf-8")
    except Exception:
        continue

    # 1. 403을 직접 발생시키는 코드 검색
    if "403" in txt or "HTTP_403_FORBIDDEN" in txt:
        lines = txt.splitlines()
        for i, line in enumerate(lines):
            if "403" in line or "HTTP_403_FORBIDDEN" in line:
                # 에러를 발생시키는 키워드가 있는 라인만 출력
                if any(kw in line for kw in ["raise", "HTTPException", "status_code", "return"]):
                    print(f"🚨 [403 코드] {p}:{i+1}")
                    print(f"   {line.strip()}\n")

    # 2. /saju/daily 경로를 처리하는 라우터 검색
    if "saju/daily" in txt or "/daily" in txt:
        # 라우터 데코레이터 근처만 출력
        lines = txt.splitlines()
        for i, line in enumerate(lines):
            if "@router" in line or "@app" in line:
                # 주변 5줄 확인
                context = "\n".join(lines[i:i+5])
                if "daily" in context.lower():
                    print(f"📍 [/saju/daily 라우터] {p}")
                    print(f"   {line.strip()}")
                    # 다음 줄에 함수 정의가 있으면 출력
                    if i+1 < len(lines) and "def " in lines[i+1]:
                        print(f"   {lines[i+1].strip()}\n")
                    else:
                        print()

print("\n✅ 검색 완료. 위에 출력된 403 코드가 범인일 가능성이 높습니다.")