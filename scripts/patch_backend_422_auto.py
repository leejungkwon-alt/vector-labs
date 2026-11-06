# scripts/patch_backend_422_auto.py
"""
백엔드 Pydantic 스키마 파일을 자동으로 찾아 extra="ignore"를 추가하는 스크립트
- 사용법:
    python scripts/patch_backend_422_auto.py            # 미리보기
    python scripts/patch_backend_422_auto.py --apply    # 실제 적용
"""
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

# 1. BaseModel과 birth_date(또는 birth_time)가 포함된 파이썬 파일 탐색
candidates = []
for p in Path(".").rglob("*.py"):
    if any(x in p.parts for x in ["venv", "node_modules", ".git", "__pycache__"]):
        continue
    try:
        txt = p.read_text(encoding="utf-8")
        if "BaseModel" in txt and ("birth_date" in txt or "birth_time" in txt):
            candidates.append(p)
    except Exception:
        pass

if not candidates:
    print("❌ 'BaseModel'과 'birth_date'가 포함된 파이썬 파일을 찾지 못했습니다.")
    print("   백엔드 폴더가 다르거나 다른 이름을 사용 중일 수 있습니다.")
    sys.exit(1)

print(f"🔎 후보 파일 {len(candidates)}개 발견:")
for p in candidates:
    print(f"   - {p}")

# 2. 파일별 패치 적용
for p in candidates:
    original = p.read_text(encoding="utf-8")
    txt = original
    
    # ConfigDict import 추가
    if "ConfigDict" not in txt:
        if "from pydantic import" in txt:
            txt = re.sub(r"from\s+pydantic\s+import\s+([^\(\n]+)", r"from pydantic import \1, ConfigDict", txt, count=1)
        else:
            txt = "from pydantic import ConfigDict\n" + txt

    # class Xxx(BaseModel): 다음 줄에 model_config 추가
    lines = txt.splitlines()
    out_lines = []
    for i, line in enumerate(lines):
        out_lines.append(line)
        if re.match(r"^class\s+\w+\s*\(\s*BaseModel\s*\):", line):
            # 이미 model_config가 있는지 확인
            has_config = False
            for next_line in lines[i+1:i+5]:
                if "model_config" in next_line:
                    has_config = True
                    break
            if not has_config:
                out_lines.append('    model_config = ConfigDict(extra="ignore")')

    txt = "\n".join(out_lines)

    if txt != original:
        if APPLY:
            p.write_text(txt, encoding="utf-8")
            print(f"✅ 패치 완료: {p}")
        else:
            print(f"🧪 미리보기 (변경 예정): {p}")

if not APPLY:
    print("\n🧪 미리보기 모드입니다. 실제로 적용하려면 --apply 플래그를 추가하세요.")