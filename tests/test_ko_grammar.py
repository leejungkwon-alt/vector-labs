"""한국어 콘텐츠 문법·번역 손상 회귀 방지."""
import json
import pathlib

KO_DATA = pathlib.Path("app/services/content/data/ko")

# 어간 + '땅의 기운'은 문법 파괴 (지지여야 함)
BAD_PATTERNS = [
    # '지지→땅의 기운' 손상 (동사 어미)
    "땅의 기운하", "땅의 기운해", "땅의 기운할", "땅의 기운한",
    "땅의 기운했", "땅의 기운합", "땅의 기운면", "땅의 기운면서",
    "땅의 기운고", "땅의 기운든", "땅의 기운라",
    # '지지→땅의 기운' 손상 (조사)
    "땅의 기운와", "땅의 기운는", "땅의 기운를",
    "땅의 기운가", "땅의 기운로",
    # 어간 복합
    "부러땅의 기운", "이어땅의 기운", "채워땅의 기운",
    "빚땅의 기운", "빠땅의 기운", "단단해땅의 기운", "가땅의 기운",
    # 별건
    "케미은",
]


def test_ko_content_no_verb_stem_corruption():
    for f in KO_DATA.glob("*.json"):
        text = f.read_text(encoding="utf-8")
        for pat in BAD_PATTERNS:
            assert pat not in text, f"{f.name}: 손상 패턴 '{pat}'"


def test_ko_content_json_valid():
    for f in KO_DATA.glob("*.json"):
        json.loads(f.read_text(encoding="utf-8"))