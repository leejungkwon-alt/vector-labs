#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FIX-21-c: PaymentModal.tsx 에 queryClient 훅 주입.
컴포넌트 시그니처 6패턴 대응:
  1) export default function X(...) {
  2) export function X(...) {
  3) function X(...) {
  4) const X = (...) => {
  5) const X: React.FC<...> = (...) => {
  6) export default X; + 별도 function X

클래스 컴포넌트면 실패 -> 수동 안내 (Rules of Hooks 위반 방지).
"""
from __future__ import annotations
import argparse, re, shutil, sys
from datetime import datetime
from pathlib import Path

TARGET = Path("frontend/src/components/PaymentModal.tsx")
APPLY = False


def P(s):
    try: print(s)
    except UnicodeEncodeError: print(s.encode("ascii", "replace").decode("ascii"))


def read(p): return p.read_text(encoding="utf-8")


def backup_write(p, s):
    if not APPLY: return
    bak = p.with_suffix(p.suffix + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S"))
    shutil.copy2(p, bak)
    p.write_text(s, encoding="utf-8")
    P(f"[BAK] {bak.name}")


def dump(p, head=60):
    lines = read(p).splitlines()
    P(f"--- {p.name} (앞 {head}줄) ---")
    for i, ln in enumerate(lines[:head], 1):
        P(f"  {i:>3}| {ln}")
    P("  ...")


def already_has_hook(src: str) -> bool:
    return bool(re.search(r"const\s+queryClient\s*=\s*useQueryClient\s*\(\s*\)", src))


def find_component_open(src: str) -> re.Match | None:
    """컴포넌트 함수 본문 시작 `{` 위치."""
    patterns = [
        # 1) export default function X(...) {   (arrow body 있는 경우 포함)
        r"export\s+default\s+function\s+\w+\s*\([^)]*\)[^{]*\{",
        # 2) export function X(...) {
        r"export\s+function\s+\w+\s*\([^)]*\)[^{]*\{",
        # 3) function X(...) {
        r"^function\s+\w+\s*\([^)]*\)[^{]*\{",
        # 4) const X = (...) => {
        r"const\s+\w+\s*=\s*\([^)]*\)\s*=>\s*\{",
        # 5) const X: React.FC<...> = (...) => {
        r"const\s+\w+\s*:\s*React\.FC[^=]*=\s*\([^)]*\)\s*=>\s*\{",
        # 6) const X = (props) => {  (single arg)
        r"const\s+\w+\s*=\s*\(?[A-Za-z_]\w*\)?\s*=>\s*\{",
    ]
    for pat in patterns:
        m = re.search(pat, src, re.MULTILINE)
        if m:
            return m
    return None


def main() -> int:
    global APPLY
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dump", action="store_true")
    args = ap.parse_args()
    APPLY = args.apply

    P("=" * 68)
    P(f"TARGET = {TARGET.resolve()}   MODE = {'APPLY' if APPLY else 'DRY'}")
    P("=" * 68)

    if not TARGET.exists():
        P(f"[FAIL] {TARGET} 없음"); return 1

    src = read(TARGET)

    if args.dump:
        dump(TARGET)

    if already_has_hook(src):
        P("[SKIP] queryClient hook 이미 삽입됨")
        if args.dump:
            # 현재 28줄 근처 재확인
            P("\n--- 현재 28줄 근처 ---")
            lines = src.splitlines()
            for i in range(max(0, 20), min(len(lines), 40)):
                mark = ">>" if i == 27 else "  "
                P(f"  {mark}{i+1:>3}| {lines[i]}")
        return 0

    # import 보강 (useQueryClient)
    if "useQueryClient" not in src:
        if re.search(r"from ['\"]@tanstack/react-query['\"]", src):
            src = re.sub(
                r"import\s*\{([^}]*)\}\s*from\s*(['\"]@tanstack/react-query['\"]);",
                lambda m: "import { " + ", ".join(sorted(set(
                    [s.strip() for s in m.group(1).split(",") if s.strip()] + ["useQueryClient"]
                ))) + f" }} from {m.group(2)};",
                src, count=1,
            )
        else:
            src = "import { useQueryClient } from '@tanstack/react-query';\n" + src
        P("[FIX] useQueryClient import 추가")

    m = find_component_open(src)
    if not m:
        P("[MANUAL] 컴포넌트 시그니처를 못 찾음 (클래스 컴포넌트일 수 있음)")
        P("  -> 아래 dump를 붙여주세요:")
        dump(TARGET)
        return 1

    insert_pos = m.end()
    snippet = "\n  const queryClient = useQueryClient();"
    new_src = src[:insert_pos] + snippet + src[insert_pos:]

    # 사후 검증: import + hook + 사용처 일관성
    if "useQueryClient" not in new_src:
        P("[FAIL] useQueryClient import 누락"); return 1
    if not re.search(r"const\s+queryClient\s*=\s*useQueryClient\s*\(\s*\)", new_src):
        P("[FAIL] hook 삽입 실패"); return 1

    backup_write(TARGET, new_src)
    P(f"[{'OK' if APPLY else 'DRY'}] 컴포넌트 열린 중괄호 뒤에 hook 삽입")
    P(f"  match: {m.group(0)[:70]!r}")
    P(f"  insert at line {src[:insert_pos].count(chr(10)) + 1}")
    if not APPLY:
        P("\n>> 적용: python fix_frontend_v4.py --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())