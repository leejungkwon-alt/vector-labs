import pathlib
import unicodedata
from app.services.content.loader import load_pack

day_pillar = "丙寅"
norm_pillar = unicodedata.normalize("NFC", day_pillar)

# 1. 경로 확인
path = pathlib.Path("app/services/content/loader.py").resolve().parent / "data" / "ko" / f"core_pillars/{norm_pillar}.json"
print(f"파일 존재 여부: {path.exists()}")
print(f"탐색 경로: {path}")

# 2. 로더 확인
try:
    res = load_pack("ko", f"core_pillars/{norm_pillar}")
    print(f"✅ 로드 성공! 이름: {res.get('name')}")
except Exception as e:
    print(f"❌ 로드 실패: {e}")