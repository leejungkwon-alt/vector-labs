# scripts/fix_portal_email_extraction.py
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
BILLING_PATH = Path("app/api/v1/endpoints/billing.py")

if not BILLING_PATH.exists():
    print(f"❌ 파일을 찾을 수 없습니다: {BILLING_PATH}")
    sys.exit(1)

txt = BILLING_PATH.read_text(encoding="utf-8")

# 기존 /portal 엔드포인트의 email 추출 부분을 찾아서 교체
old_snippet = '    email = user.get("email")'
new_snippet = '''    # dict와 객체 타입을 모두 지원하도록 안전하게 이메일 추출
    email = None
    if isinstance(user, dict):
        email = user.get("email") or user.get("user_email")
    else:
        email = getattr(user, "email", None) or getattr(user, "user_email", None)'''

if old_snippet in txt:
    txt = txt.replace(old_snippet, new_snippet, 1)
    print("✅ billing.py의 이메일 추출 로직 보강 완료")
else:
    # 만약 이전 패치로 인해 코드가 다르게 되어 있다면, /portal 엔드포인트 자체를 재작성
    import re
    # /portal 엔드포인트 블록을 찾아서 통째로 교체
    pattern = r'@router\.get\("/portal"\).*?(?=@router|$)'
    new_endpoint = '''@router.get("/portal")
async def get_customer_portal(user=Depends(get_current_user)):
    """Lemon Squeezy 고객 포털(Signed URL) 반환"""
    from app.services.lemonsqueezy_client import get_customer_portal_url
    
    # dict와 객체 타입을 모두 지원하도록 안전하게 이메일 추출
    email = None
    if isinstance(user, dict):
        email = user.get("email") or user.get("user_email")
    else:
        email = getattr(user, "email", None) or getattr(user, "user_email", None)
        
    if not email:
        raise HTTPException(status_code=400, detail="User email required")
    
    portal_url = await get_customer_portal_url(email)
    if not portal_url:
        raise HTTPException(status_code=404, detail="No active subscription found")
        
    return {"url": portal_url}

'''
    txt = re.sub(pattern, new_endpoint, txt, flags=re.DOTALL)
    print("✅ billing.py의 /portal 엔드포인트 전체 재작성 완료")

if not APPLY:
    print("\n🧪 미리보기 모드입니다. 실제로 적용하려면 --apply 플래그를 추가하세요.")
    sys.exit(0)

BILLING_PATH.write_text(txt, encoding="utf-8")
print("🎉 패치 적용 완료")