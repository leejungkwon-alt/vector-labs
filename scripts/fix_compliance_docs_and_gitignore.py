#!/usr/bin/env python3
"""
scripts/fix_compliance_docs_and_gitignore.py

테스트 2건 실패 원인 복구:

1. docs/privacy-policy.{ko,en}.md, docs/privacy-manifest.md 재생성
   - cleanup_project.py가 docs/를 지운 부작용 복구
   - 이미 있으면 건드리지 않음

2. .gitignore를 UTF-8로 재인코딩
   - Add-Content가 CP949(한국어 Windows)로 저장한 문제 해결
   - 원본 백업 후 UTF-8로 재작성
   - 한국어 주석은 유지하되 ASCII로 안전하게 정리
"""
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

# ---------- 1) docs 재생성 ----------
PRIVACY_KO = """# 개인정보 처리방침 (한국어)

최종 개정일: 2026-10-20

본 개인정보 처리방침은 SAJU(Vector Labs, 이하 "서비스")가 제공하는 사주 기반 자기 이해 리포트 서비스에 적용됩니다.

## 1. 수집하는 정보
- **출생 정보**: 생년월일, 출생 시간(선택), 출생지, 성별
- **인증 정보**: 익명 세션 ID, 소셜 로그인 식별자(Apple/Google/Kakao 연동 시)
- **푸시 토큰**: 선택적 알림 수신용 기기 토큰

## 2. 수집 목적
- 사주 명식 계산 및 리포트 생성
- 개인화된 콘텐츠 제공
- 푸시 알림 발송 (선택적)
- 서비스 품질 개선

## 3. 보관 기간
- 계정 삭제 시까지 보관
- 계정 삭제 시 30일 이내 완전 파기
- 결제 기록은 관련 법령에 따라 5년 보관

## 4. 제3자 제공
- **제공하지 않습니다.** 단, 다음 예외:
  - 사용자가 소셜 로그인을 선택한 경우 해당 플랫폼
  - 결제 처리 시 결제 대행사

## 5. 이용자의 권리
- 개인정보 열람, 정정, 삭제 요청 가능
- 계정 삭제: 앱 내 설정 → 계정 삭제
- 문의: privacy@vectorlabs.example

## 6. 아동의 개인정보
- 만 14세 미만 아동의 개인정보는 수집하지 않습니다.

## 7. 안전성 확보 조치
- 전송 구간 TLS 암호화
- 비밀번호 미저장 (소셜 로그인만)
- 정기적 보안 감사

## 8. 고지의 의무
- 본 방침 변경 시 서비스 내 공지
"""

PRIVACY_EN = """# Privacy Policy (English)

Last updated: 2026-10-20

This Privacy Policy applies to the SAJU (Vector Labs) service, which provides a self-insight report based on Four Pillars (Saju) analysis.

## 1. Information We Collect
- **Birth data**: date of birth, time of birth (optional), place of birth, gender
- **Authentication**: anonymous session ID, social login identifier (Apple/Google/Kakao)
- **Push tokens**: optional device tokens for notifications

## 2. How We Use Information
- Calculate the Four Pillars chart and generate reports
- Provide personalized content
- Send push notifications (optional)
- Improve service quality

## 3. Retention
- Kept until account deletion
- Fully destroyed within 30 days of account deletion
- Payment records retained for 5 years per applicable law

## 4. Third Parties
- **We do not share your personal data.** Exceptions:
  - The social platform you choose to log in with
  - Payment processors when you purchase

## 5. Your Rights
- Access, correct, or delete your data
- Delete your account: Settings → Delete account
- Contact: privacy@vectorlabs.example

## 6. Children
- We do not knowingly collect data from children under 14.

## 7. Security
- TLS encryption in transit
- No password storage (social login only)
- Regular security audits

## 8. Changes
- Material changes will be announced in-app.
"""

PRIVACY_MANIFEST = """# Apple Privacy Manifest 요약

> App Store 제출 시 `PrivacyInfo.xcprivacy` 파일에 매핑할 항목 정리.

## NSPrivacyTracking
- `false` — 추적(tracking) 없음

## NSPrivacyCollectedDataTypes
| 데이터 유형 | Linked to user | Tracking | 목적 |
|---|---|---|---|
| `NSPrivacyCollectedDataTypeDateOfBirth` | yes | no | App Functionality |
| `NSPrivacyCollectedDataTypeSensitiveInfo` | yes | no | App Functionality |
| `NSPrivacyCollectedDataTypeCoarseLocation` | yes | no | App Functionality |
| `NSPrivacyCollectedDataTypeUserID` | yes | no | App Functionality |

## NSPrivacyAccessedAPITypes
| API 카테고리 | 이유 |
|---|---|
| `NSPrivacyAccessedAPICategoryUserDefaults` | `CA92.1` |
| `NSPrivacyAccessedAPICategoryFileTimestamp` | `C617.1` |

## 참고
- 실제 매니페스트는 `app.json`의 `expo.ios.privacyManifests` 필드에도 반영되어 있습니다.
"""

DOCS_FILES = {
    "privacy-policy.ko.md": PRIVACY_KO,
    "privacy-policy.en.md": PRIVACY_EN,
    "privacy-manifest.md": PRIVACY_MANIFEST,
}


def create_docs() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    for name, content in DOCS_FILES.items():
        p = DOCS / name
        if p.exists():
            print(f"  [--] docs/{name}: 이미 존재")
            continue
        p.write_text(content, encoding="utf-8", newline="\n")
        print(f"  [OK] docs/{name} 생성")


# ---------- 2) .gitignore UTF-8 재인코딩 ----------
def fix_gitignore() -> None:
    p = ROOT / ".gitignore"
    if not p.exists():
        print("  [!!] .gitignore 없음")
        return

    raw = p.read_bytes()

    # 이미 UTF-8로 읽히면 skip
    try:
        raw.decode("utf-8")
        print("  [--] .gitignore: 이미 UTF-8")
        return
    except UnicodeDecodeError:
        pass

    # CP949 등으로 저장된 경우 재디코딩
    text = None
    for enc in ("cp949", "euc-kr", "latin-1"):
        try:
            text = raw.decode(enc)
            print(f"  [OK] .gitignore: {enc} → UTF-8 재인코딩")
            break
        except UnicodeDecodeError:
            continue

    if text is None:
        print("  [!!] .gitignore: 디코딩 실패, 백업만 남기고 skip")
        return

    # 백업
    bak = p.with_suffix(p.suffix + f".bak_{TS}")
    shutil.copy2(p, bak)
    print(f"  [backup] {bak.name}")

    # BOM 제거, LF 정규화
    text = text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
    p.write_text(text, encoding="utf-8", newline="\n")


# ---------- main ----------
def main() -> None:
    print("=" * 60)
    print("  컴플라이언스 테스트 2건 복구")
    print("=" * 60)

    print("\n[1] docs/ 재생성")
    create_docs()

    print("\n[2] .gitignore UTF-8 재인코딩")
    fix_gitignore()

    print("\n" + "=" * 60)
    print("  완료. 다음 명령으로 검증하세요:")
    print("    python -m pytest tests/test_compliance.py -q")
    print("=" * 60)


if __name__ == "__main__":
    main()