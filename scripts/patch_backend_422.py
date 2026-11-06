# scripts/patch_backend_422.py
# FastAPI Pydantic 모델에 extra="ignore" 설정을 추가하는 스크립트
# (실제 스키마 파일 경로는 프로젝트 구조에 맞게 수정 필요)

from pathlib import Path
import re
import sys

# 예상 스키마 파일 경로 (실제 경로로 수정하세요)
SCHEMA_FILE = Path("backend/app/schemas/birth_info.py")
APPLY = "--apply" in sys.argv

if not SCHEMA_FILE.exists():
    print(f"❌ 파일을 찾을 수 없습니다: {SCHEMA_FILE}")
    print("   실제 스키마 파일 경로로 SCHEMA_FILE 변수를 수정해주세요.")
    sys.exit(1)

original = SCHEMA_FILE.read_text(encoding="utf-8")
txt = original

# 1. ConfigDict import 추가 (없는 경우)
if "ConfigDict" not in txt:
    txt = txt.replace("from pydantic import BaseModel", "from pydantic import BaseModel, ConfigDict")

# 2. model_config = ConfigDict(extra="ignore") 추가 (클래스 정의 직후)
# 간단한 휴리스틱: 첫 번째 'class Xxx(BaseModel):' 다음 줄에 삽입
pattern = r"(class \w+\(BaseModel\):)\n"
if not re.search(r'model_config\s*=\s*ConfigDict\(extra="ignore"\)', txt):
    txt = re.sub(pattern, r'\1\n    model_config = ConfigDict(extra="ignore")\n', txt, count=1)

if txt == original:
    print("✅ 변경 사항이 없습니다 (이미 설정되었거나 패턴을 찾지 못함).")
    sys.exit(0)

if not APPLY:
    print("🧪 미리보기 모드입니다. 실제로 적용하려면 --apply 플래그를 추가하세요.")
    print(f"   변경될 파일: {SCHEMA_FILE}")
    # 변경 사항 미리보기 (diff)
    import difflib
    diff = difflib.unified_diff(original.splitlines(), txt.splitlines(), lineterm="")
    print("\n".join(list(diff)[:20]))
    sys.exit(0)

SCHEMA_FILE.write_text(txt, encoding="utf-8")
print(f"🎉 패치 완료: {SCHEMA_FILE}")