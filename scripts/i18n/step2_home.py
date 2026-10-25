#!/usr/bin/env python3
"""Step 2: home.tsx — useT 적용 및 하드코딩 한국어 2건 치환."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import apply_patches, print_footer

TARGET = "frontend/app/(tabs)/home.tsx"

PATCHES = [
    # 1) import 추가 (기존 SAJU-PATCH 주석 뒤에)
    (
        'import { useLanguageStore } from "@/store/languageStore"; // SAJU-PATCH:api-lang\n',
        'import { useLanguageStore } from "@/store/languageStore"; // SAJU-PATCH:api-lang\n'
        'import { useT } from "@/i18n";\n',
        "import { useT }",
    ),
    # 2) useT 훅 선언
    (
        '  const lang = useLanguageStore((s) => s.lang); // SAJU-PATCH:lang-decl\n',
        '  const lang = useLanguageStore((s) => s.lang); // SAJU-PATCH:lang-decl\n'
        '  const t = useT();\n',
        "const t = useT()",
    ),
    # 3) 로딩 메시지
    (
        '인생 설계도를 분석 중입니다...',
        '{t("home.loading")}',
        "로딩 메시지 → t(home.loading)",
    ),
    # 4) "요약" 섹션 타이틀
    (
        '>요약</Text>',
        '>{t("home.summary")}</Text>',
        '섹션 타이틀 "요약" → t(home.summary)',
    ),
]


def main() -> int:
    print(f"[step2] {TARGET}")
    print("-" * 62)
    applied, skipped = apply_patches(TARGET, PATCHES)
    print(f"\n결과: 적용 {applied} / 건너뜀 {skipped}")
    print_footer("step2", "i18n(step2): home.tsx useT 적용")
    return 0 if applied > 0 else 1


if __name__ == "__main__":
    sys.exit(main())