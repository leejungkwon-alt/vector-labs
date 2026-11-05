#!/usr/bin/env python3
"""
저장소 정리 (삭제 X → _cleanup_trash/ 로 '이동', 폴더 구조 유지, 언제든 되돌릴 수 있음)

  python cleanup_repo.py            # dry-run: 옮길 목록과 용량만 출력
  python cleanup_repo.py --apply    # 실제로 이동

대상: 백업/스냅샷/1회성 패치 스크립트/리뷰 산출물/미사용 복사본.
앱 런타임이 읽는 파일(app/**, frontend/app|src, data/poems.json, 콘텐츠 data/*/*.json)은 건드리지 않음.
"""
import fnmatch, shutil, sys
from pathlib import Path

APPLY = "--apply" in sys.argv
ROOT = Path(".").resolve()
TRASH = ROOT / "_cleanup_trash"

DIRS = [                       # 통째로 이동
    ".review_backups", "backups", "review_export",
    "app/services/content/data/_bak_quarantine",
    "scripts/archive",         # 1회성 i18n/보안 패치 스크립트 모음 (이미 적용 완료된 것들)
]
GLOBS = [                      # 파일명 패턴 (어느 폴더에 있든)
    "*.bak", "*.bak.*", "*.bak_*", "*.broken", "*.pre_align*", "*.pre_autofix*", "*.pre_v2", "*.pre_final",
    "*.orig", "*.rej",
]
FILES = [                      # 루트의 1회성 산출물 / 미사용 파일
    "backtrans_review.txt", "backtrans_report.py", "translation_review.md", "i18n_audit_report.txt",
    "report_dump.txt", "names_dump.txt",
    "translations_p0.json", "translations_p1.json", "translations_p2.json",
    "test_stevejobs_en.json", "test_stevejobs_es.json", "test_stevejobs_ja.json",
    "test_stevejobs_ko.json", "test_stevejobs_zh_cn.json",
    "frontend/src/components/sections/shared copy.tsx",   # 어디서도 import 안 함
    "frontend/Expo-Go-58.0.4.apk",                        # 바이너리 (Git 에 넣을 이유 없음)
]
KEEP_PARTS = {"node_modules", ".git", "_cleanup_trash"}

def size(p: Path) -> int:
    if p.is_file(): return p.stat().st_size
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())

targets = []
for d in DIRS:
    if (ROOT / d).exists(): targets.append(ROOT / d)
for f in FILES:
    if (ROOT / f).exists(): targets.append(ROOT / f)
for p in ROOT.rglob("*"):
    if KEEP_PARTS & set(p.relative_to(ROOT).parts): continue
    if p.is_file() and any(fnmatch.fnmatch(p.name, g) for g in GLOBS):
        if not any(str(p).startswith(str(t) + "/") or str(p).startswith(str(t) + "\\") or p == t for t in targets):
            targets.append(p)

total = 0
for t in sorted(set(targets)):
    s = size(t); total += s
    rel = t.relative_to(ROOT)
    print(f"{s/1024:10.0f} KB  {rel}")
    if APPLY:
        dst = TRASH / rel; dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(t), str(dst))
print(f"\n합계 {total/1024/1024:.1f} MB, 항목 {len(set(targets))}개 " + ("이동 완료 → _cleanup_trash/" if APPLY else "(dry-run, --apply 로 실행)"))
