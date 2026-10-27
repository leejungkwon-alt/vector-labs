#!/usr/bin/env python3
"""
es 번역 파이프라인 v3.
핵심 개선:
1. 스로틀: Google 250ms/req (4 req/sec, 안전)
2. Strict save: TRANSLATE_FAIL이 하나라도 있으면 파일 저장 X (거짓 성공 방지)
3. 캐시: 재실행 시 성공분은 스킵 → 실패분만 재시도
4. --max-consec-fail: 연속 실패 5회 → 안전 중단 (차단 회피)
5. 백엔드: google(기본) / deepl(선택)
"""
import argparse, hashlib, json, random, re, sys, time
from datetime import datetime
from pathlib import Path

try:
    from deep_translator import GoogleTranslator
except ImportError:
    print("pip install deep-translator"); sys.exit(1)
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

# --- 백엔드 설정 ---
BACKEND_CONFIG = {
    "google": {"min_interval": 0.25, "max_consec_fail": 5},
    "deepl":  {"min_interval": 0.10, "max_consec_fail": 10},
}

_last_call = [0.0]
_consec_fail = [0]

def _throttle(interval):
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
    def __init__(self, backend):
        self.backend = backend
        self.cfg = BACKEND_CONFIG[backend]
        if backend == "google":
            self._impl = GoogleTranslator(source="en", target="es")
        elif backend == "deepl":
            import os
            key = os.getenv("DEEPL_AUTH_KEY", "").strip()
            if not key:
                raise SystemExit("❌ DEEPL_AUTH_KEY 환경변수 필요 (또는 --backend=google)")
            self._impl = GoogleTranslator(source="en", target="es")  # placeholder
            # 실제로는 deep-translator의 deepl 백엔드 사용:
            from deep_translator import DeeplTranslator
            self._impl = DeeplTranslator(api_key=key, source="en", target="es", use_free_api=True)
        else:
            raise ValueError(backend)

    def translate(self, text):
        if not text.strip(): return text
        k = _key(text)
        if k in _cache: return _cache[k]
        if _consec_fail[0] >= self.cfg["max_consec_fail"]:
            raise RuntimeError(f"연속 실패 {_consec_fail[0]}회 — 안전 중단")
        _throttle(self.cfg["min_interval"])
        try:
            out = self._impl.translate(text)
            if not out:
                raise RuntimeError("empty result")
            _cache[k] = out
            _consec_fail[0] = 0
            return out
        except Exception as e:
            _consec_fail[0] += 1
            # 재시도 1회 (2~4초 후)
            time.sleep(2 + random.uniform(0, 2))
            try:
                _throttle(self.cfg["min_interval"] * 2)
                out = self._impl.translate(text)
                if out:
                    _cache[k] = out
                    _consec_fail[0] = 0
                    return out
            except Exception:
                pass
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
    rev = {v: k.split(":", 1)[1] for k, v in sent.items()}
    return SENTINEL_RE.sub(lambda m: rev.get(m.group(0), m.group(0)), text)


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
            return node  # 원본 유지 (저장은 안 됨)
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

    # --- Strict save: translate 실패가 하나라도 있으면 저장 X ---
    if trans_fails:
        print(f"  🚫 {len(trans_fails)} translation failures → 저장 취소 (다음 실행에서 캐시로 재시도)")
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
    ap.add_argument("--backend", default="google", choices=["google", "deepl"])
    a = ap.parse_args()

    _load_cache()
    files = sorted(p.name for p in EN_DIR.glob("*.json")) if a.all else a.files
    if not files: print("--files 또는 --all"); return 2

    try:
        tr = _Translator(a.backend)
    except SystemExit as e:
        print(e); return 2

    modes = _mode_names()
    ok = fail = 0
    for f in files:
        try:
            if process(f, tr, modes, a.dry_run): ok += 1
            else: fail += 1
        finally:
            _save_cache()  # 매 파일마다 캐시 저장 (중단 대비)
    print(f"\n결과: ok={ok}, fail={fail}")
    print("→ 재실행 시 캐시로 실패분만 이어서 처리")
    if REVIEW.exists(): print(f"리뷰 큐: {REVIEW}")
    return 0 if fail == 0 else 1

if __name__ == "__main__":
    sys.exit(main())