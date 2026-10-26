#!/usr/bin/env python3
"""
로컬 백엔드에 접속하여 프리미엄 테스트 계정을 생성하고 토큰을 발급합니다.
"""
import json
import sys
import urllib.request

BASE_URL = "http://127.0.0.1:8000/api/v1"

def main():
    print("=" * 60)
    print("[테스트 계정 생성] 프리미엄(Subscription) 권한 부여")
    print("=" * 60)

    # 1. 익명 계정 생성
    try:
        req = urllib.request.Request(f"{BASE_URL}/auth/anonymous", method="POST")
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            token = data["access_token"]
            user_id = data["user"]["id"]
            print(f"  [1] 익명 계정 생성 완료 (ID: {user_id})")
    except Exception as e:
        print(f"❌ 백엔드 서버가 켜져 있는지 확인하세요 (uvicorn...): {e}")
        return 1

    # 2. 가상 결제(IAP)로 구독자 업그레이드
    try:
        payload = json.dumps({
            "product_id": "sub_monthly_299",
            "receipt": "mock_valid_receipt"
        }).encode("utf-8")
        
        req = urllib.request.Request(
            f"{BASE_URL}/auth/me/purchase",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            method="POST"
        )
        with urllib.request.urlopen(req) as res:
            print("  [2] 프리미엄(Subscription) 결제 처리 완료")
    except Exception as e:
        print(f"❌ 결제 처리 실패: {e}")
        return 1

    print("\n" + "=" * 60)
    print("✅ 프리미엄 계정 생성 완료!")
    print("=" * 60)
    print("브라우저에 아래 토큰을 복사해서 적용하세요:\n")
    print(f"{token}\n")
    print("=" * 60)
    print("👉 적용 방법 (Chrome/Edge 기준):")
    print("  1. 앱 화면에서 F12 (개발자 도구) 열기")
    print("  2. 'Application' (애플리케이션) 탭 -> 'Local Storage' 클릭")
    print("  3. 주소(localhost:8081) 선택 후, 오른쪽 빈 공간에 우클릭 -> Add Item")
    print("  4. Key 에는 'saju.access_token' 입력")
    print("  5. Value 에는 위에 출력된 토큰 복사해서 붙여넣기")
    print("  6. 브라우저 새로고침 (F5)")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())