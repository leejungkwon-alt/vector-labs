#!/usr/bin/env python3
"""Step 3: daily.tsx — useT 적용 및 하드코딩 한국어 치환.

주의: subscriberOnlyBody 원문에는 리터럴 '\\n'(백슬래시+n) 두 글자가 포함되어 있어
화면에 그대로 '\\n'이 노출되는 기존 버그가 있습니다.
이번 치환으로 t()가 반환하는 실제 개행(newline)으로 바뀌어 화면이 정상화됩니다.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import apply_patches, print_footer

TARGET = "frontend/app/(tabs)/daily.tsx"

PATCHES = [
    # 1) import useT
    (
        'import { useLanguageStore } from "@/store/languageStore";\n',
        'import { useLanguageStore } from "@/store/languageStore";\n'
        'import { useT } from "@/i18n";\n',
        "import { useT }",
    ),
    # 2) useT 훅 선언 (lang 선언 바로 다음)
    (
        '  const lang = useLanguageStore((s) => s.lang);\n',
        '  const lang = useLanguageStore((s) => s.lang);\n'
        '  const t = useT();\n',
        "const t = useT()",
    ),
    # 3) 사용자 정보 로딩
    (
        '사용자 정보를 불러오는 중...',
        '{t("daily.loadingUser")}',
        "daily.loadingUser",
    ),
    # 4) 사주 정보 없음 타이틀
    (
        '>사주 정보가 없습니다.</Text>',
        '>{t("daily.noProfileTitle")}</Text>',
        "daily.noProfileTitle",
    ),
    # 5) 사주 정보 없음 안내
    (
        '>홈 탭에서 사주 정보를 먼저 입력해 주세요.</Text>',
        '>{t("daily.noProfileDetail")}</Text>',
        "daily.noProfileDetail",
    ),
    # 6) 7일 로딩 메시지
    (
        '7일간의 기운을 읽어오고 있습니다...',
        '{t("daily.loading")}',
        "daily.loading",
    ),
    # 7) 구독자 전용 타이틀
    (
        '>구독자 전용 기능입니다</Text>',
        '>{t("daily.subscriberOnlyTitle")}</Text>',
        "daily.subscriberOnlyTitle",
    ),
    # 8) 구독자 전용 본문 (리터럴 \n 두 글자 → 실제 개행으로 교체)
    (
        '              매일 아침 당신의 기운을 읽어주는\\n데일리 에너지 서비스입니다.\\n프리미엄으로 업그레이드하고\\n7일치 흐름을 미리 확인하세요.\n',
        '              {t("daily.subscriberOnlyBody")}\n',
        "daily.subscriberOnlyBody (+실제 개행 렌더링)",
    ),
    # 9) 업그레이드 버튼
    (
        '>프리미엄 업그레이드</Text>',
        '>{t("daily.upgrade")}</Text>',
        "daily.upgrade",
    ),
    # 10) 일반 에러 타이틀
    (
        '>오류가 발생했습니다</Text>',
        '>{t("daily.errorTitle")}</Text>',
        "daily.errorTitle",
    ),
    # 11) 히어로 서브텍스트
    (
        '>앞으로 7일간의 일운입니다.</Text>',
        '>{t("daily.heroSub")}</Text>',
        "daily.heroSub",
    ),
    # 12) 집중 라벨
    (
        '<Text style={{fontWeight: "700"}}>집중:</Text>',
        '<Text style={{fontWeight: "700"}}>{t("daily.focus")}:</Text>',
        "daily.focus",
    ),
    # 13) 주의 라벨
    (
        '<Text style={{fontWeight: "700"}}>주의:</Text>',
        '<Text style={{fontWeight: "700"}}>{t("daily.watch")}:</Text>',
        "daily.watch",
    ),
]


def main() -> int:
    print(f"[step3] {TARGET}")
    print("-" * 62)
    applied, skipped = apply_patches(TARGET, PATCHES)
    print(f"\n결과: 적용 {applied} / 건너뜀 {skipped}")
    print_footer("step3", "i18n(step3): daily.tsx useT 적용 + \\n 렌더링 수정")
    return 0 if applied > 0 else 1


if __name__ == "__main__":
    sys.exit(main())