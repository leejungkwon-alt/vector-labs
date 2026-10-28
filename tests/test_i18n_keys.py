import json
from pathlib import Path
import pytest

DATA_DIR = Path(__file__).parent.parent / "app" / "services" / "content" / "data"
LANGS = ["ko", "ja", "zh_cn", "es"]

def get_all_keys(data, prefix=""):
    """JSON 구조에서 모든 키의 경로(Path)를 추출합니다."""
    keys = {}
    if isinstance(data, dict):
        for k, v in data.items():
            keys.update(get_all_keys(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(data, list):
        keys[prefix] = "LIST"
        for i, v in enumerate(data):
            keys.update(get_all_keys(v, f"{prefix}[{i}]"))
    else:
        keys[prefix] = type(data).__name__
    return keys

@pytest.mark.parametrize("lang", LANGS)
def test_language_keys_match_en(lang):
    """en 언어팩과 다른 언어팩 간의 키 구조가 일치하는지 검증합니다."""
    en_dir = DATA_DIR / "en"
    lang_dir = DATA_DIR / lang

    for en_file in en_dir.rglob("*.json"):
        rel_path = en_file.relative_to(en_dir)
        lang_file = lang_dir / rel_path

        if not lang_file.exists():
            pytest.fail(f"[{lang}] 파일 누락: {rel_path}")

        en_data = json.loads(en_file.read_text(encoding="utf-8"))
        lang_data = json.loads(lang_file.read_text(encoding="utf-8"))

        en_keys = get_all_keys(en_data)
        lang_keys = get_all_keys(lang_data)

        missing_in_lang = set(en_keys.keys()) - set(lang_keys.keys())
        if missing_in_lang:
            # 리스트 구조 차이(단일 항목 vs 3개 리스트)인 경우도 여기서 잡힙니다.
            pytest.fail(f"[{lang}] {rel_path} 에 키 누락: {list(missing_in_lang)[:5]} 외 {len(missing_in_lang)}개")

        type_mismatch = []
        for k in set(en_keys.keys()) & set(lang_keys.keys()):
            if en_keys[k] != lang_keys[k]:
                type_mismatch.append(f"{k} (EN: {en_keys[k]}, {lang.upper()}: {lang_keys[k]})")
        
        if type_mismatch:
            pytest.fail(f"[{lang}] {rel_path} 타입/구조 불일치: {type_mismatch[:5]} 외")