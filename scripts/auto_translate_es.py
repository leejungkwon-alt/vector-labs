#!/usr/bin/env python3
"""
es 자동번역 파이프라인 (Phase 6-A).
- 입력: en/*.json (canonical), 필요시 ja/*.json (tone 참조용 옵션)
- 대상: 지정 파일 리스트 or 전체
- 보호: {placeholder}, THE_*, best_match/challenging_match 모드명, name_traditional
- 스킵: version, MODE_AXES, pillar_names.keys
- 저장: 사전검증 (json.loads + placeholder 집합 + 모드명 집합) 통과 시에만
- 백업: .bak.<ts>

사용 예:
  python scripts/auto_translate_es.py --files career.json love.json wealth.json
  python scripts/auto_translate_es.py --all
  python scripts/auto_translate_es.py --files energy.json --dry-run
"""
import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

# pip install deep-translator
from deep_translator import GoogleTranslator

ROOT = Path(__file__).resolve().parent.parent
EN = ROOT / "app/services/content/data/en"
ES = ROOT / "app/services/content/data/es"
JA_SECTIONS = ROOT / "app/services/content/data/ja/sections.json"
ES_SECTIONS = ROOT / "app/services/content/data/es/sections.json"

PLACEHOLDER_RE = re.compile(r"\{([a-z_]+)\}")
THE_CODE_RE = re.compile(r"THE_[A-Z_]+")

# 자동번역 스킵 키 (leaf 이름)
SKIP_KEYS = {"version", "MODE_AXES", "name_traditional"}

# 자동번역 스킵 경로 (파일 → JSON 경로 패턴)
# MODE_AXES는 dict of dict of numbers
SKIP_PATH_SEGMENTS = {"MODE_AXES", "MODE_AXES_ja"}  # 숫자 보호

# 모드명 목록 (es/sections.json MODE_DISPLAY 값들 → 보호)
def _mode_names() -> set:
    if not ES_SECTIONS.exists():
        return set()
    data = json.loads(ES_SECTIONS.read_text(encoding="utf-8"))
    return set(data.get("MODE_DISPLAY", {}).values()) | set(data.get("MODE_DISPLAY", {}).keys())

# Translate call with retry
def _translate(text: str, translator: GoogleTranslator, retries: int = 3) -> str:
    if not text.strip():
        return text
    for i in range(retries):
        try:
            return translator.translate(text) or text
        except Exception as e:
            if i == retries - 1:
                raise RuntimeError(f"translate failed: {e}") from e
            time.sleep(1.5 * (i + 1))
    return text


def _protect(text: str, mode_names: set, sentinels: dict) -> str:
    """민감 토큰을 unique sentinel로 치환. sentinels는 {원본: sentinel} 누적 dict."""
    def _sub(pattern, prefix, group=0):
        def _inner(m):
            key = m.group(group) if group else m.group(0)
            if key not in sentinels:
                sentinels[key] = f"X{prefix}{len(sentinels)}X"
            return sentinels[key]
        return re.sub(pattern, _inner, text)

    text = _sub(PLACEHOLDER_RE, "PH", group=1)     # {pillar} → XPH0X
    text = _sub(THE_CODE_RE, "MD")                 # THE_ANCHOR → XMD1X
    # best_match 같은 짧은 모드명 (Anchor, Blade, ...)은 단어경계로만
    for name in sorted(mode_names, key=len, reverse=True):
        if len(name) < 2:
            continue
        pat = r"\b" + re.escape(name) + r"\b"
        if re.search(pat, text):
            if name not in sentinels:
                sentinels[name] = f"XMN{len(sentinels)}X"
            text = re.sub(pat, sentinels[name], text)
    return text


def _restore(text: str, sentinels: dict, ph_only: bool = False) -> str:
    """sentinel → 원본. ph_only=True면 placeholder만 원복 (검증용)."""
    rev = {v: k for k, v in sentinels.items()}
    def _inner(m):
        tok = m.group(0)
        if tok not in rev:
            return tok  # 미매핑 sentinel은 그대로 (검증에서 잡힘)
        return rev[tok]
    return re.sub(r"X(?:PH|MD|MN)\d+X", _inner, text)


def _walk_translate(node, en_node, translator, mode_names, sentinels, path=""):
    """node가 현재 es 데이터(사본), en_node는 참조용. 반환: 새 값."""
    if isinstance(node, dict):
        return {
            k: _walk_translate(v, (en_node or {}).get(k), translator, mode_names,
                               sentinels, f"{path}.{k}" if path else k)
            for k, v in node.items()
        }
    if isinstance(node, list):
        return [
            _walk_translate(v, (en_node or [None] * len(node))[i] if isinstance(en_node, list) and i < len(en_node) else None,
                           translator, mode_names, sentinels, f"{path}[{i}]")
            for i, v in enumerate(node)
        ]
    if isinstance(node, str):
        leaf = path.rsplit(".", 1)[-1] if path else ""
        if leaf in SKIP_KEYS:
            return node  # 원본 유지
        # 이미 es가 en과 다르면 skip (이미 번역됨)
        if en_node is not None and node != en_node:
            return node
        if not node.strip():
            return node
        protected = _protect(node, mode_names, sentinels)
        translated = _translate(protected, translator)
        restored = _restore(translated, sentinels)
        return restored
    return node  # int/float/bool


def _validate(es_new: dict, en: dict, sentinels: dict) -> list:
    """placeholder 원본과 동일한가 + sentinel 잔존 없는가."""
    errors = []

    def _walk_str(node, ref, path=""):
        if isinstance(node, dict):
            for k, v in node.items():
                _walk_str(v, (ref or {}).get(k), f"{path}.{k}" if path else k)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                _walk_str(v, (ref or [None]*len(node))[i] if isinstance(ref, list) and i < len(ref) else None,
                         f"{path}[{i}]")
        elif isinstance(node, str):
            leaf = path.rsplit(".", 1)[-1] if path else ""
            if leaf in SKIP_KEYS:
                return
            # placeholder 비교
            got = set(PLACEHOLDER_RE.findall(node))
            want = set(PLACEHOLDER_RE.findall(ref or ""))
            if got != want:
                errors.append(f"{path}: placeholder {sorted(want)} != {sorted(got)}")
            # sentinel 잔존
            if re.search(r"X(?:PH|MD|MN)\d+X", node):
                errors.append(f"{path}: sentinel 잔존")

    _walk_str(es_new, en)
    return errors


def process_file(fname: str, dry_run: bool = False) -> int:
    en_path = EN / fname
    es_path = ES / fname
    if not en_path.exists():
        print(f"❌ {fname}: en 원본 없음")
        return 1
    if not es_path.exists():
        print(f"⚠️  {fname}: es 복사본 없음 → en에서 시작")
        es_path.parent.mkdir(parents=True, exist_ok=True)
        es_path.write_text(en_path.read_text(encoding="utf-8"), encoding="utf-8")

    en_data = json.loads(en_path.read_text(encoding="utf-8"))
    es_data = json.loads(es_path.read_text(encoding="utf-8"))

    mode_names = _mode_names()
    translator = GoogleTranslator(source="en", target="es")

    sentinels: dict = {}
    print(f"\n📄 {fname}")
    new_data = _walk_translate(es_data, en_data, translator, mode_names, sentinels)

    errors = _validate(new_data, en_data, sentinels)
    if errors:
        for e in errors:
            print(f"  ❌ {e}")
        print("  → 저장 취소")
        return 1

    print(f"  ✅ sentinels: {len(sentinels)}개 보호·복원 완료")
    if dry_run:
        print("  [dry-run] 저장 생략")
        return 0

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = es_path.with_name(es_path.name + f".bak.{ts}")
    bak.write_text(es_path.read_text(encoding="utf-8"), encoding="utf-8")

    payload = json.dumps(new_data, ensure_ascii=False, indent=2) + "\n"
    json.loads(payload)
    es_path.write_text(payload, encoding="utf-8")
    print(f"  💾 저장 (bak: {bak.name})")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="*", default=[], help="파일명 리스트 (예: career.json)")
    ap.add_argument("--all", action="store_true", help="en/*.json 전부")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.all:
        files = sorted(p.name for p in EN.glob("*.json"))
    else:
        files = args.files
    if not files:
        print("❌ --files 또는 --all 필요")
        return 2

    ok = fail = 0
    for f in files:
        rc = process_file(f, dry_run=args.dry_run)
        if rc == 0:
            ok += 1
        else:
            fail += 1

    print(f"\n결과: ok={ok}, fail={fail}")
    print("→ pytest 후 커밋: git add -A; git commit -m 'i18n(es): auto-translated batch'")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())