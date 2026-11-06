# scripts/fix_backend_email.py
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

ROUTER_PATH = Path("app/auth/router.py")
BILLING_PATH = Path("app/api/v1/endpoints/billing.py")

# ---------------- 1. router.py 수정 (_user_public 및 link_provider) ----------------
if ROUTER_PATH.exists():
    txt = ROUTER_PATH.read_text(encoding="utf-8")

    # 1-1. _user_public 에 email 필드 추가
    old_public = '''        "social_provider": user.get("social_provider"),
        "social_subject": user.get("social_subject"),
        "created_at": user["created_at"],
    }'''
    new_public = '''        "social_provider": user.get("social_provider"),
        "social_subject": user.get("social_subject"),
        "created_at": user["created_at"],
        "email": user.get("email"),
    }'''
    if "email" not in txt:
        txt = txt.replace(old_public, new_public, 1)
        print("✅ [라우터] _user_public 에 email 필드 추가 완료")

    # 1-2. link_provider 에서 받아온 email을 저장하도록 수정
    # (identity 딕셔너리에 email이 들어있다고 가정)
    old_link = '''        updated = get_repository().link_social_identity(
            user["id"], identity["provider"], identity["subject"],
        )'''
    new_link = '''        updated = get_repository().link_social_identity(
            user["id"], identity["provider"], identity["subject"],
            email=identity.get("email"), # 👈 이메일도 함께 저장!
        )'''
    if old_link in txt:
        txt = txt.replace(old_link, new_link, 1)
        print("✅ [라우터] link_provider 에 email 저장 로직 추가 완료")
        
    if APPLY:
        ROUTER_PATH.write_text(txt, encoding="utf-8")

# ---------------- 2. billing.py 수정 (에러 방어 및 로깅) ----------------
if BILLING_PATH.exists():
    txt = BILLING_PATH.read_text(encoding="utf-8")
    
    # /portal 엔드포인트 안전하게 재작성
    pattern = r'@router\.get\("/portal"\).*?(?=@router|$)'
    new_endpoint = '''@router.get("/portal")
async def get_customer_portal(user: dict = Depends(get_current_user)):
    """Lemon Squeezy 고객 포털(Signed URL) 반환"""
    from app.services.lemonsqueezy_client import get_customer_portal_url
    
    # 유저 객체에 이메일이 있는지 안전하게 확인
    email = user.get("email")
    
    if not email:
        # 이메일이 없으면 400 대신 명확한 에러 메시지 반환
        print(f"DEBUG: User {user.get('id')} has no email in DB.")
        raise HTTPException(
            status_code=400, 
            detail="User has no email address. Please link a social account (Google) first."
        )
    
    portal_url = await get_customer_portal_url(email)
    if not portal_url:
        raise HTTPException(status_code=404, detail="No active subscription found for this email.")
        
    return {"url": portal_url}
'''
    txt = re.sub(pattern, new_endpoint, txt, flags=re.DOTALL)
    print("✅ [결제] billing.py 의 /portal 엔드포인트 방어 코드 적용 완료")

    if APPLY:
        BILLING_PATH.write_text(txt, encoding="utf-8")

if not APPLY:
    print("\n🧪 미리보기 모드입니다. 실제로 적용하려면 --apply 플래그를 추가하세요.")
else:
    print("\n🎉 백엔드 패치가 모두 완료되었습니다.")