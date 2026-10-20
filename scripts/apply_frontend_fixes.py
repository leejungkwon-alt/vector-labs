#!/usr/bin/env python3
"""
scripts/apply_frontend_fixes.py

frontend/ quick wins 3건을 한 번에 적용합니다.

  1. frontend/app/(tabs)/home.tsx       → target_year 동적화
  2. frontend/app/index.tsx             → 죽은 timeout 폴백 제거 (전체 재작성)
  3. frontend/app/(tabs)/compatibility.tsx → 프로필 없을 때 버튼 disabled

안전장치:
  - 이미 적용된 파일은 skip (idempotent, 여러 번 실행해도 안전)
  - 각 수정 대상 파일은 `*.bak_<timestamp>`로 자동 백업
  - 매칭 실패 시 그 파일만 건너뛰고 나머지 진행
  - BOM 상태 보존 (원본에 BOM이 있으면 유지, 없으면 없이 저장)
  - 쓰기는 `newline='\\n'` 강제 → git diff 노이즈 방지

사용법:
    python scripts/apply_frontend_fixes.py --dry-run     # 미리보기 (파일 안 건드림)
    python scripts/apply_frontend_fixes.py               # 적용 + git commit + push
    python scripts/apply_frontend_fixes.py --no-commit   # 적용만 (git 건너뜀)
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

STATS: dict[str, list[str]] = {"applied": [], "skipped": [], "failed": []}


# -------------------- I/O 헬퍼 --------------------

def read_text(p: Path) -> tuple[str, bool]:
    """UTF-8(+BOM) 텍스트로 읽고, BOM 존재 여부도 반환. 개행은 \\n 정규화."""
    raw = p.read_bytes()
    had_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig") if had_bom else raw.decode("utf-8")
    # CRLF → LF 정규화 (git diff 노이즈 방지)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text, had_bom


def write_text(p: Path, text: str, had_bom: bool) -> None:
    """BOM 상태를 보존하며 UTF-8, LF로 저장."""
    data = text.encode("utf-8")
    if had_bom:
        data = b"\xef\xbb\xbf" + data
    p.write_bytes(data)


def backup(p: Path) -> Path:
    dst = p.with_suffix(p.suffix + f".bak_{TS}")
    shutil.copy2(p, dst)
    return dst


# -------------------- 패턴 치환 --------------------

def replace_exact(text: str, old: str, new: str, label: str) -> tuple[str, bool]:
    """정확히 한 번 매칭될 때만 치환. 매칭 0회 → 이미 적용됐는지 확인 후 skip/fail."""
    n = text.count(old)
    if n == 0:
        if new in text:
            STATS["skipped"].append(f"{label}: 이미 적용됨")
        else:
            STATS["failed"].append(f"{label}: 대상 문자열을 찾지 못함")
        return text, False
    if n > 1:
        STATS["failed"].append(f"{label}: 대상 문자열이 {n}번 등장 (안전상 skip)")
        return text, False
    return text.replace(old, new), True


# -------------------- 수정 1: home.tsx --------------------

def fix_home(dry: bool) -> bool:
    p = FRONTEND / "app" / "(tabs)" / "home.tsx"
    if not p.exists():
        STATS["failed"].append(f"home.tsx: 파일 없음 ({p})")
        return False

    text, had_bom = read_text(p)

    old = 'queryFn: () => api.report({ ...profile, target_year: 2026, lang: "ko" }),'
    new = (
        'queryFn: () => api.report({\n'
        '    ...profile,\n'
        '    target_year: new Date().getFullYear(),\n'
        '    lang: "ko",\n'
        '  }),'
    )

    new_text, changed = replace_exact(text, old, new, "home.tsx: target_year 동적화")
    if not changed:
        return False
    if dry:
        STATS["applied"].append("home.tsx: target_year 동적화 (dry-run)")
        return True

    backup(p)
    write_text(p, new_text, had_bom)
    STATS["applied"].append("home.tsx: target_year 동적화")
    return True


# -------------------- 수정 2: index.tsx --------------------

NEW_INDEX = '''import { useEffect } from "react";
import { ActivityIndicator, View, Text } from "react-native";
import { router } from "expo-router";
import { useAuthStore } from "@/store/authStore";
import { useProfileStore } from "@/store/profileStore";

export default function Index() {
  const ready = useAuthStore((s) => s.ready);
  const profileReady = useProfileStore((s) => s.ready);
  const profile = useProfileStore((s) => s.profile);

  useEffect(() => {
    if (!ready || !profileReady) return;
    router.replace(profile ? "/(tabs)/home" : "/birth-input");
  }, [ready, profileReady, profile]);

  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#FDF6EE" }}>
      <Text style={{ fontSize: 32, fontWeight: "700", color: "#E85D2F", marginBottom: 16 }}>SAJU</Text>
      <ActivityIndicator color="#E85D2F" />
      <Text style={{ marginTop: 12, color: "#7A6A5C" }}>Preparing your session...</Text>
    </View>
  );
}
'''


def fix_index(dry: bool) -> bool:
    p = FRONTEND / "app" / "index.tsx"
    if not p.exists():
        STATS["failed"].append(f"index.tsx: 파일 없음 ({p})")
        return False

    text, had_bom = read_text(p)

    # 이미 수정된 상태 감지
    if "timeoutId" not in text and "hasError" not in text:
        STATS["skipped"].append("index.tsx: 이미 적용됨")
        return False

    if dry:
        STATS["applied"].append("index.tsx: 죽은 timeout 폴백 제거 (dry-run)")
        return True

    backup(p)
    write_text(p, NEW_INDEX, had_bom)
    STATS["applied"].append("index.tsx: 죽은 timeout 폴백 제거 (전체 재작성)")
    return True


# -------------------- 수정 3: compatibility.tsx --------------------

def fix_compat(dry: bool) -> bool:
    p = FRONTEND / "app" / "(tabs)" / "compatibility.tsx"
    if not p.exists():
        STATS["failed"].append(f"compatibility.tsx: 파일 없음 ({p})")
        return False

    text, had_bom = read_text(p)
    changed = False

    # 3-1: handleCalculate 가드
    old_calc = '''  const handleCalculate = async () => {
    setIsCalculated(true);
    await refetch();
  };'''
    new_calc = '''  const handleCalculate = async () => {
    if (!myProfile) return;
    setIsCalculated(true);
    await refetch();
  };'''
    text, c1 = replace_exact(
        text, old_calc, new_calc, "compatibility.tsx: handleCalculate 가드"
    )
    changed = changed or c1

    # 3-2: 버튼 disabled + opacity
    old_btn = '''      <TouchableOpacity style={styles.nextBtn} onPress={handleCalculate}>
        <Text style={styles.nextBtnText}>케미 보기</Text>
      </TouchableOpacity>'''
    new_btn = '''      <TouchableOpacity
        style={[styles.nextBtn, !myProfile && { opacity: 0.4 }]}
        onPress={handleCalculate}
        disabled={!myProfile}
      >
        <Text style={styles.nextBtnText}>케미 보기</Text>
      </TouchableOpacity>'''
    text, c2 = replace_exact(
        text, old_btn, new_btn, "compatibility.tsx: 버튼 disabled"
    )
    changed = changed or c2

    if not changed:
        return False
    if dry:
        STATS["applied"].append("compatibility.tsx: 버튼 disabled (dry-run)")
        return True

    backup(p)
    write_text(p, text, had_bom)
    STATS["applied"].append("compatibility.tsx: 버튼 disabled")
    return True


# -------------------- git --------------------

def run_git(args: list[str]) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def print_stats() -> None:
    for key, icon in (("applied", "OK"), ("skipped", "--"), ("failed", "!!")):
        if STATS[key]:
            print(f"\n[{icon}] {key}:")
            for item in STATS[key]:
                print(f"  - {item}")


# -------------------- main --------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="파일 변경 없이 미리보기")
    ap.add_argument("--no-commit", action="store_true", help="적용만, git 건너뜀")
    args = ap.parse_args()

    print("=" * 60)
    print("  frontend/ quick wins 3건")
    print("=" * 60)

    any_changed = False
    any_changed |= fix_home(args.dry_run)
    any_changed |= fix_index(args.dry_run)
    any_changed |= fix_compat(args.dry_run)

    print_stats()

    if args.dry_run:
        print("\n[dry-run] 실제 파일 변경 없음")
        sys.exit(0 if not STATS["failed"] else 1)

    if not any_changed:
        print("\n변경 사항 없음 — git commit 건너뜀")
        sys.exit(0)

    # 변경된 파일 목록
    changed_paths = [
        "frontend/app/(tabs)/home.tsx",
        "frontend/app/index.tsx",
        "frontend/app/(tabs)/compatibility.tsx",
        "scripts/dump_codebase.py",  # 아직 커밋 안 됐으면 함께
    ]

    if args.no_commit:
        print("\n--no-commit: git 작업 건너뜀")
        print("수동 커밋: git add " + " ".join(changed_paths))
        sys.exit(0)

    print("\n[git] add → commit → push")
    try:
        for path in changed_paths:
            run_git(["git", "add", path])

        # 실제로 스테이징된 게 있는지 확인
        staged = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()

        if not staged:
            print("[git] 스테이징된 변경 없음 — commit 건너뜀")
            sys.exit(0)

        print(f"[git] staged files:\n{staged}")

        run_git([
            "git", "commit", "-m",
            "fix: frontend quick wins + dump_codebase UTF-8 fix\n\n"
            "- frontend/home.tsx: target_year를 현재 연도로 동적화\n"
            "- frontend/index.tsx: 죽은 timeout 폴백 제거 (라우팅만 유지)\n"
            "- frontend/compatibility.tsx: 프로필 없을 때 버튼 disabled\n"
            "- scripts/dump_codebase.py: 한국어 UTF-8 텍스트를 바이너리로\n"
            "  오판하던 is_binary() 로직 수정",
        ])
        run_git(["git", "push", "origin", "main"])
        print("\n[done] 커밋 + 푸시 완료")
    except subprocess.CalledProcessError as e:
        print(f"\n[!!] git 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()