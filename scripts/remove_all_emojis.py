import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 프론트엔드의 모든 tsx 파일을 순회하며 이모지 제거
files = list((ROOT / "frontend" / "src").rglob("*.tsx")) + list((ROOT / "frontend" / "app").rglob("*.tsx"))

emoji_pattern = re.compile(
    "["
    "\U0001F300-\U0001F5FF"  # 기호 및 그림 문자
    "\U0001F600-\U0001F64F"  # 이모티콘
    "\U0001F680-\U0001F6FF"  # 교통 및 지도
    "\U0001F700-\U0001F77F"  # 연금술 기호
    "\U0001F780-\U0001F7FF"  # 기하학적 도형 확장
    "\U0001F800-\U0001F8FF"  # 보충 기호
    "\U0001F900-\U0001F9FF"  # 보충 이모티콘
    "\U0001FA00-\U0001FA6F"  # 체스 기호 등
    "\U0001FA70-\U0001FAFF"  # 기호 및 그림 문자 확장
    "\U0001F1E6-\U0001F1FF"  # 국기
    "\U00002700-\U000027BF"  # 딩벳
    "\U00002600-\U000026FF"  # 기타 기호 (여기에 ☒ 등이 포함될 수 있음)
    "]+",
    flags=re.UNICODE
)

for p in files:
    t = p.read_text(encoding="utf-8")
    # 이모지 제거
    new_t = emoji_pattern.sub("", t)
    
    # 혹시 남아있을 수 있는 특정 문자 제거
    for char in ["☒", "🔒", "🔐", "❌", "✨", "💡", "🚀", "🎯"]:
        new_t = new_t.replace(char, "")
        
    if new_t != t:
        p.write_text(new_t, encoding="utf-8")
        print(f"[OK] 이모지 제거 완료: {p.name}")

print("모든 프론트엔드 파일의 이모지 제거가 완료되었습니다.")
