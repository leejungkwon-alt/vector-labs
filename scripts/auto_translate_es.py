#!/usr/bin/env python3
"""
es 완전 자동번역 파이프라인 v4 (requests 직접 통신).
- 라이브러리 의존성 제거: deep-translator 대신 requests로 DeepL API 직접 호출
- 네트워크 및 API 키 작동 확인 완료 (HTTP 200, Hola)
- QA 3층, 캐시, Strict save, 스로틀 모두 유지
"""
import argparse, hashlib, json, os, random, re, sys, time
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("pip install requests"); sys.exit(1)
try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 42
except ImportError:
    print("pip install langdetect"); sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
EN_DIR = ROOT / "app/services/content/data/en"
ES_DIR = ROOT / "app/services/content/data/es"
CACHE = ROOT / "scripts/.cache/es_translation_cache.json"
REVIEW = ROOT / "scripts/.cache/es_review_queue.txt"

PLACEHOLDER_RE = re.compile(r"\{([a-z_]+)\}")
THE_CODE_RE = re.compile(r"THE_[A-Z_]+")
SENTINEL_RE = re.compile(r"X(?:PH|MD|MN)\d+X")
EN_STOP_RE = re.compile(
    r"\b(?:the|and|of|with|that|from|this|these|those|which"
    r"|would|could|should|have|has|been|are|were|was|will"
    r"|your|their)\b", re.IGNORECASE,
)

SKIP_LEAF = {"version", "name_traditional"}
SKIP_PATH_SEG = {"MODE_DISPLAY", "MODE_AXES"}

_last_call = [0.0]
_consec_fail = [0]

def _throttle(interval=0.15):  # DeepL free: 10 req/sec
    elapsed = time.time() - _last_call[0]
    if elapsed < interval:
        time.sleep(interval - elapsed)
    _last_call[0] = time.time()

_cache = {}
def _load_cache():
    if CACHE.exists(): _cache.update(json.loads(CACHE.read_text("utf-8")))
def _save_cache():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(_cache, ensure_ascii=False, indent=0), "utf-8")
def _key(t): return hashlib.sha256(t.encode("utf-8")).hexdigest()

class _Translator:
    def __init__(self):
        self.key = os.environ.get("DEEPL_AUTH_KEY", "").strip()
        if not self.key:
            raise SystemExit("❌ DEEPL_AUTH_KEY 환경변수가 설정되지 않았습니다.")
        self.url = "https://api-free.deepl.com/v2/translate"
        self.headers = {"Authorization": f"DeepL-Auth-Key {self.key}"}

    def translate(self, text):
        if not text.strip(): return text
        k = _key(text)
        if k in _cache: return _cache[k]
        if _consec_fail[0] >= 5:
            raise RuntimeError(f"연속 실패 {_consec_fail[0]}회 — 안전 중단")
        
        _throttle()
        try:
            r = requests.post(
                self.url, headers=self.headers,
                data={"text": text, "target_lang": "ES"},
                timeout=10
            )
            if r.status_code == 200:
                out = r.json()["translations"][0]["text"]
                _cache[k] = out
                _consec_fail[0] = 0
                return out
            elif r.status_code == 456:
                raise RuntimeError("DeepL 월간 한도 초과")
            else:
                raise RuntimeError(f"HTTP {r.status_code}: {r.text[:100]}")
        except Exception as e:
            _consec_fail[0] += 1
            time.sleep(2 + random.uniform(0, 2))
            raise RuntimeError(str(e)) from e


def _mode_names():
    p = ES_DIR / "sections.json"
    if not p.exists(): return set()
    d = json.loads(p.read_text("utf-8")).get("MODE_DISPLAY", {})
    return set(d.values()) | set(d.keys())


def _protect(text, modes, sent):
    def ph(m):
        k = "ph:" + m.group(1)
        if k not in sent: sent[k] = f"XPH{len(sent)}X"
        return sent[k]
    text = PLACEHOLDER_RE.sub(ph, text)
    def md(m):
        k = "md:" + m.group(0)
        if k not in sent: sent[k] = f"XMD{len(sent)}X"
        return sent[k]
    text = THE_CODE_RE.sub(md, text)
    for name in sorted(modes, key=len, reverse=True):
        if len(name) < 2: continue
        pat = r"\b" + re.escape(name) + r"\b"
        if re.search(pat, text):
            k = "mn:" + name
            if k not in sent: sent[k] = f"XMN{len(sent)}X"
            text = re.sub(pat, sent[k], text)
    return text


def _restore(text, sent):
    def _sub(m):
        tok = m.group(0)
        for k, v in sent.items():
            if v == tok:
                prefix, val = k.split(":", 1)
                return f"{{{val}}}" if prefix == "ph" else val
        return tok
    return SENTINEL_RE.sub(_sub, text)

def _lint(en, es, path):
    w = []
    if len(es) >= 40:
        try:
            lang = detect(es)
            if lang == "en": w.append(f"{path}: langdetect=en")
            elif lang not in ("es", "ca", "gl", "pt"):
                w.append(f"{path}: langdetect={lang}")
        except Exception: pass
    if EN_STOP_RE.search(es): w.append(f"{path}: English word leftover")
    if "  " in es: w.append(f"{path}: double space")
    if len(es) > 20 and en[:1].isupper() and es[:1].islower():
        w.append(f"{path}: leading lowercase")
    return w


def _walk(node, ref, tr, modes, sent, warns, review, trans_fails, path="", skip=False):
    if isinstance(node, dict):
        return {k: _walk(v, (ref or {}).get(k), tr, modes, sent, warns, review,
                        trans_fails, f"{path}.{k}" if path else k,
                        skip or (k in SKIP_PATH_SEG)) for k, v in node.items()}
    if isinstance(node, list):
        return [_walk(v, ((ref or [])[i] if isinstance(ref, list) and i < len(ref) else None),
                      tr, modes, sent, warns, review, trans_fails, f"{path}[{i}]", skip)
                for i, v in enumerate(node)]
    if isinstance(node, str):
        if skip: return node
        leaf = path.rsplit(".", 1)[-1].split("[")[0] if path else ""
        if leaf in SKIP_LEAF: return node
        if ref is not None and node != ref: return node  # 이미 번역됨
        if not node.strip(): return node
        try:
            protected = _protect(node, modes, sent)
            translated = tr.translate(protected)
        except RuntimeError as e:
            warns.append(f"{path}: TRANSLATE_FAIL {e}")
            trans_fails.append(path)
            return node
        restored = _restore(translated, sent)
        ws = _lint(node, restored, path)
        if ws: warns.extend(ws); review.append((path, node, restored))
        return restored
    return node


def _structural_validate(new, ref, path=""):
    errs = []
    def walk(n, r, p):
        if isinstance(n, dict):
            for k, v in n.items(): walk(v, (r or {}).get(k), f"{p}.{k}" if p else k)
        elif isinstance(n, list):
            for i, v in enumerate(n): walk(v, (r or [])[i] if isinstance(r, list) and i < len(r) else None, f"{p}[{i}]")
        elif isinstance(n, str):
            leaf = p.rsplit(".", 1)[-1].split("[")[0] if p else ""
            if leaf in SKIP_LEAF: return
            if set(PLACEHOLDER_RE.findall(r or "")) != set(PLACEHOLDER_RE.findall(n)):
                errs.append(f"{p}: placeholder mismatch")
            if SENTINEL_RE.search(n):
                errs.append(f"{p}: sentinel leak")
    walk(new, ref, path)
    return errs


def process(fname, tr, modes, dry):
    en_p = EN_DIR / fname; es_p = ES_DIR / fname
    if not en_p.exists(): print(f"❌ {fname}: en 없음"); return False
    if not es_p.exists():
        es_p.parent.mkdir(parents=True, exist_ok=True)
        es_p.write_text(en_p.read_text("utf-8"), "utf-8")
    en_d = json.loads(en_p.read_text("utf-8"))
    es_d = json.loads(es_p.read_text("utf-8"))

    sent, warns, review, trans_fails = {}, [], [], []
    print(f"\n📄 {fname}")
    try:
        new = _walk(es_d, en_d, tr, modes, sent, warns, review, trans_fails)
    except RuntimeError as e:
        print(f"  🚫 중단: {e}")
        return False

    errs = _structural_validate(new, en_d)
    if errs:
        for e in errs: print(f"  🚫 {e}")
        return False

    if trans_fails:
        print(f"  🚫 {len(trans_fails)} translation failures → 저장 취소")
        for p in trans_fails[:5]: print(f"     - {p}")
        return False

    if dry:
        print(f"  [dry-run] warnings={len(warns)}, sentinels={len(sent)}")
        return True

    payload = json.dumps(new, ensure_ascii=False, indent=2) + "\n"
    json.loads(payload)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    (es_p.with_name(es_p.name + f".bak.{ts}")).write_text(es_p.read_text("utf-8"), "utf-8")
    es_p.write_text(payload, "utf-8")

    if review:
        REVIEW.parent.mkdir(parents=True, exist_ok=True)
        with REVIEW.open("a", encoding="utf-8") as f:
            f.write(f"\n=== {fname} ===\n")
            for p, o, t in review:
                f.write(f"[{p}]\nEN: {o[:200]}\nES: {t[:200]}\n\n")

    print(f"  💾 saved (sentinels={len(sent)}, warnings={len(warns)})")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="*", default=[])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    _load_cache()
    files = sorted(p.name for p in EN_DIR.glob("*.json")) if a.all else a.files
    if not files: print("--files 또는 --all"); return 2

    try:
        tr = _Translator()
    except SystemExit as e:
        print(e); return 2

    modes = _mode_names()
    ok = fail = 0
    for f in files:
        try:
            if process(f, tr, modes, a.dry_run): ok += 1
            else: fail += 1
        finally:
            _save_cache()
    print(f"\n결과: ok={ok}, fail={fail}")
    if REVIEW.exists(): print(f"리뷰 큐: {REVIEW}")
    return 0 if fail == 0 else 1

if __name__ == "__main__":
    sys.exit(main())