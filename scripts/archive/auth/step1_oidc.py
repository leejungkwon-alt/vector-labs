#!/usr/bin/env python3
"""
scripts/auth/step1_oidc.py — P1-1 실제 OIDC 검증 (Apple / Google / Kakao)

이 파일은 "적용안(스켈레톤)"입니다.
새 세션에서 각 apply 명령의 실제 구현을 채워 넣는 방식으로 진행합니다.

------------------------------------------------------------------
[작업 개요]

현재 `app/auth/providers.py`는 `mock:<subject>` 토큰만 받습니다.
이걸 실제 OIDC(Apple/Google/Kakao) ID 토큰 검증으로 교체합니다.

[서브스텝]

  1-A. 사전요건 확인 (의존성, env, 기존 테스트)              ← 스켈레톤 구현됨
  1-B. providers.py 리팩터: provider별 검증기 분리            ← TODO
       - ProvidersError 유지
       - `verify_apple`, `verify_google`, `verify_kakao` 각각 분리
       - 개발 모드(`SAJU_ENV!=production`)에서는 `mock:` 계속 허용
  1-C. Apple OIDC (JWKS 기반)                                ← TODO
       - issuer: https://appleid.apple.com
       - audience: SAJU_APPLE_CLIENT_ID
       - JWKS: https://appleid.apple.com/auth/keys (kid 캐시)
       - 서명: RS256, pyjwt[crypto]
  1-D. Google OIDC (JWKS 기반)                               ← TODO
       - issuer: https://accounts.google.com
       - audience: SAJU_GOOGLE_CLIENT_ID
       - JWKS: https://www.googleapis.com/oauth2/v3/certs (kid 캐시)
       - 서명: RS256
  1-E. Kakao                                                  ← TODO
       - Kakao는 표준 OIDC JWKS 엔드포인트가 있으나 앱별 구성 필요.
       - 우선 토큰 조회 API(`/v2/user/me`)로 id 검증:
         - `SAJU_KAKAO_APP_KEY`(또는 admin key) 헤더
         - 응답의 `id`를 subject로 사용
       - 추후 OIDC로 승격 여지 남겨둠
  1-F. 테스트                                                  ← TODO
       - `tests/test_social_link.py`:
         - production에서 mock 거부 (이미 있음)
         - 각 provider의 verify 함수 유닛테스트 (JWKS/응답 모킹)
       - 새 파일: `tests/test_oidc_verification.py`
  1-G. 프론트엔드 통합                                         ← TODO
       - `frontend/src/store/authStore.ts`의 `linkAccount`를
         실제 SDK(expo-auth-session, expo-apple-authentication)로 교체.
       - 백엔드 계약(`/auth/link/{provider}`, `provider_token`)은 그대로.

[환경 변수]

  SAJU_APPLE_CLIENT_ID     # Apple Service ID (iOS 앱 번들 ID와 별개일 수 있음)
  SAJU_GOOGLE_CLIENT_ID    # Google OAuth 2.0 Client ID (웹/앱)
  SAJU_KAKAO_APP_KEY       # Kakao REST API key (앱 키)
  (기존) SAJU_ENV=production  ← 이 경우 mock:* 토큰은 이미 거부됨

[신규 의존성]

  requirements.txt:
    pyjwt[crypto]>=2.8.0    # 현재 pyjwt만 있음, crypto extra 필요
  (httpx, tzdata는 이미 있음)

  frontend/package.json (Step 1-G에서):
    expo-auth-session
    expo-apple-authentication
    expo-crypto

[사용법]

  python scripts/auth/step1_oidc.py plan
      → 전체 계획 표시

  python scripts/auth/step1_oidc.py verify
      → 현재 레포 상태 점검 (파일, env, 의존성, 테스트)

  python scripts/auth/step1_oidc.py apply 1-b     (TODO: 새 세션에서 채움)
  python scripts/auth/step1_oidc.py apply 1-c     (TODO)
  python scripts/auth/step1_oidc.py apply 1-d     (TODO)
  python scripts/auth/step1_oidc.py apply 1-e     (TODO)
  python scripts/auth/step1_oidc.py apply 1-f     (TODO)
  python scripts/auth/step1_oidc.py apply 1-g     (TODO)

  각 apply는 해당 서브스텝의 patch 리스트/생성 파일 리스트를 정의하고
  `_common.apply_patches` / `_common.create_file`로 실행하도록 새 세션에서 작성.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (
    ROOT,
    apply_patches,
    append_env_example,
    create_file,
    env_var_present_in_example,
    file_contains,
    print_footer,
    pyproject_has_pkg,
    run,
)

# ============================================================
# 서브스텝 정의 (새 세션에서 채움)
# ============================================================
SUBSTEPS = {
    "1-a": "사전요건 확인 (의존성, env, 기존 테스트)   [구현됨]",
    "1-b": "providers.py 리팩터 (provider별 분리)",
    "1-c": "Apple OIDC (JWKS)",
    "1-d": "Google OIDC (JWKS)",
    "1-e": "Kakao (토큰 조회 API)",
    "1-f": "테스트 (tests/test_oidc_verification.py)",
    "1-g": "프론트엔드 통합 (expo-auth-session)",
}


# ============================================================
# 1-A: 사전요건 확인 (구현됨)
# ============================================================
def verify() -> int:
    print("[verify] P1-1 OIDC 사전요건 확인")
    print("=" * 62)

    issues = 0

    def ok(msg):  print(f"✅ {msg}")
    def warn(msg): print(f"⚠️  {msg}")
    def bad(msg):  print(f"❌ {msg}"); nonlocal_issues[0] += 1
    nonlocal_issues = [0]

    # --- 파일 존재 ---
    for f, label in [
        ("app/auth/providers.py", "providers.py"),
        ("tests/test_social_link.py", "test_social_link.py"),
        ("requirements.txt", "requirements.txt"),
        (".env.example", ".env.example"),
        ("frontend/src/store/authStore.ts", "authStore.ts"),
    ]:
        if (ROOT / f).exists():
            ok(f"{label} 존재")
        else:
            bad(f"{label} 없음")

    # --- providers.py 현재 상태 ---
    if file_contains("app/auth/providers.py", "MOCK_PREFIX"):
        ok("providers.py: mock 처리 확인 (교체 대상)")
    else:
        warn("providers.py: MOCK_PREFIX 없음 — 이미 리팩터됐을 수 있음")

    if file_contains("app/auth/providers.py", "not yet implemented"):
        ok("providers.py: 'not yet implemented' 안내 확인 (교체 예정)")

    # --- requirements.txt ---
    if pyproject_has_pkg("requirements.txt", "pyjwt"):
        ok("requirements.txt: pyjwt 있음")
    else:
        bad("requirements.txt: pyjwt 없음")
    if pyproject_has_pkg("requirements.txt", "cryptography"):
        ok("requirements.txt: cryptography 있음 (RS256 서명 검증 가능)")
    else:
        warn("requirements.txt: cryptography 없음 → 1-B에서 pyjwt[crypto]로 교체 필요")
    if pyproject_has_pkg("requirements.txt", "httpx"):
        ok("requirements.txt: httpx 있음 (JWKS fetch)")
    else:
        bad("requirements.txt: httpx 없음")

    # --- env ---
    for name, purpose in [
        ("SAJU_APPLE_CLIENT_ID", "Apple Service ID"),
        ("SAJU_GOOGLE_CLIENT_ID", "Google Client ID"),
        ("SAJU_KAKAO_APP_KEY", "Kakao REST API key"),
    ]:
        if env_var_present_in_example(name):
            ok(f".env.example: {name} 있음")
        else:
            warn(f".env.example: {name} 없음 → 1-B에서 추가 예정 ({purpose})")

    # --- 프론트 의존성 ---
    pkg_json = ROOT / "frontend/package.json"
    if pkg_json.exists():
        import json
        data = json.loads(pkg_json.read_text(encoding="utf-8"))
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        if "expo-auth-session" in deps:
            ok("frontend: expo-auth-session 있음")
        else:
            warn("frontend: expo-auth-session 없음 → 1-G에서 추가 예정")
        if "expo-apple-authentication" in deps:
            ok("frontend: expo-apple-authentication 있음")
        else:
            warn("frontend: expo-apple-authentication 없음 → 1-G에서 추가 예정")

    # --- 테스트 실행 (social_link) ---
    print("-" * 62)
    print("[verify] 기존 social_link 테스트 실행...")
    rc, out = run([sys.executable, "-m", "pytest", "tests/test_social_link.py", "-q"],
                  cwd=ROOT)
    if rc == 0:
        ok("tests/test_social_link.py: 통과")
    else:
        bad("tests/test_social_link.py: 실패 (로그 확인)")
        print(out[-800:])

    print("-" * 62)
    if nonlocal_issues[0] == 0:
        print(f"🎉 사전요건 통과 ({len(SUBSTEPS) - 1}개 서브스텝 남음)")
        return 0
    print(f"❌ 이슈 {nonlocal_issues[0]}개 — 위 로그 참고")
    return 1


# ============================================================
# apply: 서브스텝별 실행 (스켈레톤 — 새 세션에서 채움)
# ============================================================
def apply_1_b():
    """
    1-B: providers.py 리팩터

    새 세션에서 아래를 채우세요:

    patches = [
        # requirements.txt: pyjwt → pyjwt[crypto]
        (
            "pyjwt>=2.8.0\n",
            "pyjwt[crypto]>=2.8.0\n",
            "requirements: pyjwt[crypto]",
        ),
        # providers.py: import httpx, jwt
        # providers.py: dispatch 구조로 리팩터
        # providers.py: verify_apple, verify_google, verify_kakao 스텁 추가
        # providers.py: verify_provider_token이 dispatch 호출하도록 수정
    ]
    apply_patches("requirements.txt", [...])
    apply_patches("app/auth/providers.py", patches)
    append_env_example({
        "SAJU_APPLE_CLIENT_ID": "Apple Service ID (Apple Developer Console)",
        "SAJU_GOOGLE_CLIENT_ID": "Google OAuth 2.0 Client ID",
        "SAJU_KAKAO_APP_KEY": "Kakao REST API key",
    })
    """
    raise NotImplementedError("1-B는 새 세션에서 구현")


def apply_1_c():
    """1-C: Apple OIDC (JWKS) — 새 세션에서 구현."""
    raise NotImplementedError("1-C는 새 세션에서 구현")


def apply_1_d():
    """1-D: Google OIDC (JWKS) — 새 세션에서 구현."""
    raise NotImplementedError("1-D는 새 세션에서 구현")


def apply_1_e():
    """1-E: Kakao (토큰 조회 API) — 새 세션에서 구현."""
    raise NotImplementedError("1-E는 새 세션에서 구현")


def apply_1_f():
    """1-F: 테스트 — 새 세션에서 구현."""
    raise NotImplementedError("1-F는 새 세션에서 구현")


def apply_1_g():
    """1-G: 프론트엔드 통합 — 새 세션에서 구현."""
    raise NotImplementedError("1-G는 새 세션에서 구현")


APPLY_DISPATCH = {
    "1-b": apply_1_b,
    "1-c": apply_1_c,
    "1-d": apply_1_d,
    "1-e": apply_1_e,
    "1-f": apply_1_f,
    "1-g": apply_1_g,
}


# ============================================================
# CLI
# ============================================================
def cmd_plan():
    print(__doc__)
    print("=" * 62)
    print("서브스텝 목록:")
    for key, desc in SUBSTEPS.items():
        print(f"  {key}  {desc}")
    print("=" * 62)
    print("다음 명령:")
    print("  python scripts/auth/step1_oidc.py verify")
    return 0


def cmd_verify():
    return verify()


def cmd_apply(step: str):
    step = step.lower().strip()
    if step not in APPLY_DISPATCH:
        print(f"❌ 알 수 없는 서브스텝: {step}")
        print(f"   사용 가능: {', '.join(APPLY_DISPATCH.keys())}")
        return 2
    try:
        APPLY_DISPATCH[step]()
    except NotImplementedError as e:
        print(f"🚧 {e}")
        print()
        print("이 스텝은 새 세션에서 채워 넣으세요.")
        print("이 파일의 apply_1_{} 함수 안에 patch 리스트를 작성하고,".format(step.split("-")[1]))
        print("_common.apply_patches / create_file / append_env_example로 실행하도록 구현합니다.")
        print()
        print("참고: 새 세션 첫 메시지에 이 스크립트 파일을 첨부하세요.")
        return 3
    print_footer(f"step1-oidc-{step}", f"auth(oidc-{step}): P1-1 진행")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="P1-1 OIDC 스켈레톤")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_plan = sub.add_parser("plan", help="계획 표시")
    p_plan.set_defaults(func=lambda _: cmd_plan())

    p_verify = sub.add_parser("verify", help="사전요건 확인")
    p_verify.set_defaults(func=lambda _: cmd_verify())

    p_apply = sub.add_parser("apply", help="서브스텝 적용")
    p_apply.add_argument("step", help="서브스텝 코드 (예: 1-b)")
    p_apply.set_defaults(func=lambda a: cmd_apply(a.step))

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())