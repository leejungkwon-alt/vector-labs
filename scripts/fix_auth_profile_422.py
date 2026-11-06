# scripts/fix_auth_profile_422.py
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

# 전체 프로젝트 루트에서 파이썬 파일 탐색
ROOT_DIR = Path(".")
patched_files = []
candidates_found = False

for p in ROOT_DIR.rglob("*.py"):
    # 불필요한 폴더 제외
    if any(part in p.parts for part in ["venv", ".venv", "node_modules", "__pycache__", ".git"]):
        continue
    
    try:
        txt = p.read_text(encoding="utf-8")
    except Exception:
        continue

    # Pydantic 모델과 birth_ 필드가 모두 있는 파일만 타겟팅
    if "BaseModel" not in txt or "birth_" not in txt:
        continue

    original = txt
    candidates_found = True
    
    # 1. ConfigDict import 보장
    if "ConfigDict" not in txt:
        if "from pydantic import" in txt:
            txt = re.sub(r"from pydantic import ([^\n]+)", r"from pydantic import \1, ConfigDict", txt, count=1)
        else:
            txt = "from pydantic import ConfigDict\n" + txt

    # 2. 클래스 블록 분석하여 model_config 추가
    lines = txt.splitlines()
    out_lines = []
    
    for i, line in enumerate(lines):
        out_lines.append(line)
        
        # BaseModel 상속 클래스 찾기
        if re.match(r"^class\s+\w+\s*\(.*BaseModel.*\):", line):
            class_text = ""
            for next_line in lines[i+1:]:
                if next_line.startswith("class ") or next_line.startswith("@") or (next_line and not next_line[0].isspace() and not next_line.startswith("#")):
                    break
                class_text += next_line + "\n"
            
            if "birth_" in class_text:
                if "model_config" not in class_text and "class Config" not in class_text:
                    out_lines.append('    model_config = ConfigDict(extra="ignore")')
                    print(f"✅ 패치 대상 발견: {p} -> {line.strip()}")

    txt = "\n".join(out_lines)

    if txt != original:
        if APPLY:
            p.write_text(txt, encoding="utf-8")
            print(f"🎉 파일 패치 완료: {p}")
        patched_files.append(p)

if not candidates_found:
    print("❌ 'BaseModel'과 'birth_'이 포함된 파이썬 파일을 전체 프로젝트에서 찾지 못했습니다.")
    print("   FastAPI 백엔드 코드가 이 폴더 안에 있는지 다시 한번 확인해주세요.")
elif not patched_files:
    print("ℹ️ 대상 파일은 찾았으나, 이미 패치가 되어있거나 수정할 클래스가 없습니다.")
elif not APPLY:
    print("\n🧪 미리보기 모드입니다. 실제로 적용하려면 --apply 플래그를 추가하세요.")