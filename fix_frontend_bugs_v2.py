#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_frontend_bugs_v2.py  —  SAJU 프론트엔드 3단계 (22-26)

v1 대비 개선:
  - --root frontend 기본
  - --apply 필수 (미지정 시 dry-run)
  - ASCII-only 로그 (Windows cp949 안전)
  - 매치 0건이면 컨텍스트 dump (수동 확인)
  - FIX-24/25 매치 없으면 안전 skip (파일 손상 방지)
"""
from __future__ import annotations
import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT: Path = Path("frontend")
APPLY: bool = False
RESULTS: list[tuple[str, str, str]] = []   # (fid, status, detail)


# ------------------------------------------------------------------ utils
def P(msg: str) -> None:
    """ASCII-safe print."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def backup_and_write(p: Path, text: str) -> None:
    if not APPLY:
        return
    bak = p.with_suffix(p.suffix + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S"))
    shutil.copy2(p, bak)
    p.write_text(text, encoding="utf-8")


def record(fid: str, status: str, detail: str = "") -> None:
    RESULTS.append((fid, status, detail))


def dump_context(p: Path, patterns: list[str], n_before: int = 2, n_after: int = 8,
                 max_hits: int = 3) -> str:
    """매치 없을 때 주변 코드 dump (비-ASCII는 ? 로 치환)."""
    lines = read(p).splitlines()
    out, hits = [], 0
    for i, line in enumerate(lines):
        if any(re.search(pat, line) for pat in patterns):
            lo, hi = max(0, i - n_before), min(len(lines), i + n_after + 1)
            out.append(f"  >> L{i+1}:")
            for j in range(lo, hi):
                out.append(f"     {j+1:>4}| {lines[j]}")
            hits += 1
            if hits >= max_hits:
                break
    if not out:
        out.append(f"  (매치 없음) 파일 앞 30줄:")
        for j, line in enumerate(lines[:30]):
            out.append(f"     {j+1:>4}| {line}")
    # ASCII-safe
    return "\n".join(s.encode("ascii", "replace").decode("ascii") for s in out)


# ------------------------------------------------------------------ FIX-22
def fix_22() -> None:
    fid = "FIX-22"
    targets = [ROOT / "app/(tabs)/compatibility.tsx", ROOT / "app/birth-input.tsx"]
    pat = re.compile(r"offsetHours\s*\*\s*15")
    for p in targets:
        if not p.exists():
            record(fid, "SKIP", f"{p} 없음"); continue
        src = read(p)
        if not pat.search(src):
            record(fid, "SKIP", f"{p.name}: 이미 정상"); continue
        new = pat.sub("0 /* FIX-22: backend handles timezone */", src)
        backup_and_write(p, new)
        record(fid, "OK" if APPLY else "DRY", f"{p.name}: offsetHours*15 -> 0")


# ------------------------------------------------------------------ FIX-21
def fix_21() -> None:
    fid = "FIX-21"
    p = ROOT / "src/components/PaymentModal.tsx"
    if not p.exists():
        record(fid, "SKIP", "PaymentModal.tsx 없음"); return
    src = read(p)
    pat = re.compile(r"(?:if\s*\(\s*typeof\s+window\s*!==\s*['\"]undefined['\"]\s*\)\s*)?"
                     r"window\.location\.reload\s*\(\s*\)\s*;?")
    if not pat.search(src):
        record(fid, "SKIP", "window.location.reload() 없음 (이미 정상)"); return

    repl = (
        "/* FIX-21: hard reload removed -> cache invalidate + bootstrap */\n"
        "        try {\n"
        "          if (typeof queryClient !== 'undefined' && queryClient) {\n"
        "            await queryClient.invalidateQueries();\n"
        "          }\n"
        "          if (typeof bootstrap === 'function') {\n"
        "            await bootstrap();\n"
        "          }\n"
        "        } catch (e) {\n"
        "          console.warn('[FIX-21] post-payment refresh failed', e);\n"
        "        }"
    )
    new = pat.sub(repl, src, count=1)

    # useQueryClient import 보강
    if "useQueryClient" not in new:
        if re.search(r"from ['\"]@tanstack/react-query['\"]", new):
            new = re.sub(r"import\s*\{([^}]*)\}\s*from\s*(['\"]@tanstack/react-query['\"]);",
                         lambda m: "import { " + ", ".join(sorted(set(
                             [s.strip() for s in m.group(1).split(",") if s.strip()] + ["useQueryClient"]
                         ))) + f" }} from {m.group(2)};", new, count=1)
        else:
            new = "import { useQueryClient } from '@tanstack/react-query';\n" + new

    # 훅 삽입
    if "const queryClient = useQueryClient()" not in new:
        m = re.search(r"(export\s+default\s+function\s+\w+\s*\([^)]*\)\s*\{)", new)
        if m:
            new = new[:m.end()] + "\n  const queryClient = useQueryClient();" + new[m.end():]

    backup_and_write(p, new)
    record(fid, "OK" if APPLY else "DRY", "reload -> invalidateQueries+bootstrap")


# ------------------------------------------------------------------ FIX-23
def fix_23() -> None:
    fid = "FIX-23"
    p = ROOT / "src/api/client.ts"
    if not p.exists():
        record(fid, "SKIP", "client.ts 없음"); return
    src = read(p)
    # BASE_URL 정의 라인만 교체 (사용처는 그대로)
    pat = re.compile(
        r"(?P<decl>const|let|var)\s+(?P<name>BASE_URL)\s*(?::\s*string\s*)?=\s*"
        r"['\"]https?://[^'\"]*(?:run\.app|cloudrun|googleapis)[^'\"]*['\"]\s*;",
    )
    if not pat.search(src):
        record(fid, "SKIP", "BASE_URL 하드코딩 매치 없음"); return
    repl = (
        "/* FIX-23: env-based (dev: localhost:8000, prod: EXPO_PUBLIC_API_URL) */\n"
        "const BASE_URL: string = (() => {\n"
        "  const env = (typeof process !== 'undefined' && process.env) ? process.env.EXPO_PUBLIC_API_URL : undefined;\n"
        "  if (env) return env;\n"
        "  if (typeof __DEV__ !== 'undefined' && __DEV__) return 'http://localhost:8000/api/v1';\n"
        "  if (typeof console !== 'undefined') console.warn('[client] EXPO_PUBLIC_API_URL not set');\n"
        "  return '';\n"
        "})();"
    )
    new = pat.sub(repl, src, count=1)
    backup_and_write(p, new)
    record(fid, "OK" if APPLY else "DRY", "BASE_URL: env-based")


# ------------------------------------------------------------------ FIX-26
def fix_26() -> None:
    fid = "FIX-26"
    targets = [ROOT / "src/components/SocialLoginModal.tsx",
               ROOT / "src/components/PaymentModal.tsx"]
    bare_alert = re.compile(r"(?<![\w.])alert\s*\(\s*([^;()]+?)\s*\)\s*;")
    for p in targets:
        if not p.exists():
            record(fid, "SKIP", f"{p.name} 없음"); continue
        src = read(p)
        if not bare_alert.search(src):
            record(fid, "SKIP", f"{p.name}: bare alert() 없음"); continue

        def _repl(m: re.Match) -> str:
            msg = m.group(1).strip()
            return (f"if (typeof Platform !== 'undefined' && Platform.OS === 'web') "
                    f"{{ window.alert({msg}); }} "
                    f"else {{ Alert.alert('알림', {msg}); }}")

        new = bare_alert.sub(_repl, src)

        # react-native import 보강 (single/double quote 모두 대응)
        rn_pat = re.compile(r"import\s*\{([^}]*)\}\s*from\s*(['\"])react-native\2;")
        m = rn_pat.search(new)
        if m:
            names = {s.strip() for s in m.group(1).split(",") if s.strip()}
            names.update({"Alert", "Platform"})
            new = rn_pat.sub(
                f"import {{ {', '.join(sorted(names))} }} from {m.group(2)}react-native{m.group(2)};",
                new, count=1)
        else:
            new = "import { Alert, Platform } from 'react-native';\n" + new

        backup_and_write(p, new)
        record(fid, "OK" if APPLY else "DRY", f"{p.name}: Platform-aware alert")


# ------------------------------------------------------------------ FIX-24/25 inspect
def inspect_24_25() -> None:
    for fid, fname, pats in [
        ("FIX-24", "app/_layout.tsx", [r"tabBarIcon", r"as\s+string", r"as\s+any", r"Tabs\.", r"<Tabs"]),
        ("FIX-25", "app/index.tsx", [r"console\.(log|info|warn)", r"\[Boot\]"]),
    ]:
        p = ROOT / fname
        if not p.exists():
            record(fid, "SKIP", f"{fname} 없음"); continue
        src = read(p)
        # 원래 목표 패턴
        if fid == "FIX-24":
            has_bad = bool(re.search(r"\(\s*color\s+as\s+(string|any)\s*\)", src))
            if not has_bad:
                record(fid, "SKIP", "color as string/any 이미 없음 (정상)")
                continue
        if fid == "FIX-25":
            has_bad = bool(re.search(r'console\.(log|info)\s*\(\s*["\']\[Boot\]', src))
            if not has_bad:
                record(fid, "SKIP", "[Boot] console.log 이미 없음 (정상)")
                continue
        # 여기 오면 수동 필요 → 컨텍스트 안내
        record(fid, "MANUAL", "패턴 존재하나 자동 치환 어려움 → 아래 dump 참고")


# ------------------------------------------------------------------ main
def main() -> int:
    global ROOT, APPLY
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="frontend")
    ap.add_argument("--apply", action="store_true", help="실제 파일 수정 (없으면 dry-run)")
    args = ap.parse_args()
    ROOT = Path(args.root).resolve()
    APPLY = args.apply

    P("=" * 68)
    P(f"ROOT  = {ROOT}")
    P(f"MODE  = {'APPLY (backup + write)' if APPLY else 'DRY-RUN'}")
    P("=" * 68)
    if not ROOT.exists():
        P(f"[FAIL] root not found: {ROOT}"); return 1

    fix_22()
    fix_21()
    fix_23()
    fix_26()
    inspect_24_25()

    P("")
    P("-" * 68)
    icon_map = {"OK": "[OK]", "DRY": "[DRY]", "SKIP": "[SKIP]", "MANUAL": "[MANUAL]"}
    for fid, status, detail in RESULTS:
        P(f"{icon_map.get(status, status):>9}  {fid:<8}  {detail}")
    P("-" * 68)
    ok = sum(1 for _, s, _ in RESULTS if s == "OK")
    dry = sum(1 for _, s, _ in RESULTS if s == "DRY")
    P(f"applied={ok}  dry_run_matched={dry}  total={len(RESULTS)}")
    if not APPLY:
        P("")
        P(">> 적용하려면: python fix_frontend_bugs_v2.py --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())