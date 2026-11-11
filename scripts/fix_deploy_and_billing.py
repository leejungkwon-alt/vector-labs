import re
import shutil
from pathlib import Path

ROOT = Path(".")
BACKUP = ROOT / "scripts" / "_backups"
BACKUP.mkdir(parents=True, exist_ok=True)

STORE_ID = "516056"
SUB_VARIANT = "2341690"
ONETIME_VARIANT = "2357370"


def read(p: Path):
    raw = p.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    return raw.decode("utf-8-sig"), bom


def write(p: Path, text: str, bom: bool):
    p.write_bytes((b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8"))


def backup(p: Path):
    shutil.copy2(p, BACKUP / (p.name + ".before_fix"))


# 1. deploy.ps1: 자리표시자를 실제 ID로
p = ROOT / "deploy.ps1"
text, bom = read(p)
orig = text
text = re.sub(r"LEMONSQUEEZY_STORE_ID=[^,\s\"`]*", f"LEMONSQUEEZY_STORE_ID={STORE_ID}", text)
text = re.sub(r"LEMONSQUEEZY_VARIANT_ID=[^,\s\"`]*", f"LEMONSQUEEZY_VARIANT_ID={SUB_VARIANT}", text)
text = re.sub(r"LEMONSQUEEZY_ONETIME_VARIANT_ID=[^,\s\"`]*", f"LEMONSQUEEZY_ONETIME_VARIANT_ID={ONETIME_VARIANT}", text)
if text != orig:
    backup(p)
    write(p, text, bom)
    print("OK   deploy.ps1: STORE/VARIANT ID 수정")
else:
    print("SKIP deploy.ps1: 변경 없음(이미 올바른 값이거나 해당 줄 없음)")

# 2. 오염 원인 스크립트 보관 처리
archive = ROOT / "scripts" / "archive"
archive.mkdir(parents=True, exist_ok=True)
for name in ("final_checkout_fix.py", "recover_env_vars.py"):
    src = ROOT / "scripts" / name
    if src.exists():
        dst = archive / name
        if dst.exists():
            dst.unlink()
        shutil.move(str(src), str(dst))
        print(f"OK   scripts/{name} -> scripts/archive/")
    else:
        print(f"SKIP scripts/{name}: 없음")

# 3. billing.py 수정
p = ROOT / "app" / "api" / "v1" / "endpoints" / "billing.py"
text, bom = read(p)
orig = text

# 3a. 구독 variant .strip()
old = 'else os.environ.get("LEMONSQUEEZY_VARIANT_ID")'
new = 'else (os.environ.get("LEMONSQUEEZY_VARIANT_ID") or "").strip()'
if old in text:
    text = text.replace(old, new)
    print("OK   billing.py: 구독 VARIANT_ID .strip() 추가")
else:
    print("SKIP billing.py: 구독 VARIANT_ID 줄을 찾지 못함(이미 수정됨?)")

# 3b. 웹훅의 1회권 variant .strip()
old = 'os.environ.get("LEMONSQUEEZY_ONETIME_VARIANT_ID", "")\n'
new = 'os.environ.get("LEMONSQUEEZY_ONETIME_VARIANT_ID", "").strip()\n'
if old in text and 'LEMONSQUEEZY_ONETIME_VARIANT_ID", "").strip()' not in text:
    text = text.replace(old, new)
    print("OK   billing.py: 웹훅 ONETIME variant .strip() 추가")
else:
    print("SKIP billing.py: 웹훅 ONETIME variant 줄 변경 없음")

# 3c. 웹훅 시크릿 .strip()
old = 'os.environ.get("LEMONSQUEEZY_WEBHOOK_SECRET", "")\n'
new = 'os.environ.get("LEMONSQUEEZY_WEBHOOK_SECRET", "").strip()\n'
if old in text and 'LEMONSQUEEZY_WEBHOOK_SECRET", "").strip()' not in text:
    text = text.replace(old, new)
    print("OK   billing.py: 웹훅 시크릿 .strip() 추가")
else:
    print("SKIP billing.py: 웹훅 시크릿 줄 변경 없음")

# 3d. 멱등 처리로 교체 (두 호출 -> 한 호출)
pat = re.compile(
    r'(?P<i>[ \t]+)repo\.add_onetime_credit\(user_id\)\r?\n'
    r'[ \t]+repo\.log_purchase\(user_id, "lemon_onetime", "lemon_squeezy"\)\r?\n'
)
if pat.search(text):
    text = pat.sub(
        lambda m: f'{m.group("i")}granted = repo.add_onetime_purchase_idempotent(user_id, order_id)\n'
                  f'{m.group("i")}logger.info("LS order_created order=%s granted=%s", order_id, granted)\n',
        text,
    )
    print("OK   billing.py: 크레딧 적립을 add_onetime_purchase_idempotent로 교체")
    if "order_id =" not in text:
        print("WARN billing.py: order_id 변수 정의를 확인하세요")
else:
    print("SKIP billing.py: add_onetime_credit + log_purchase 두 줄 패턴을 찾지 못함 (직접 확인 필요)")

if text != orig:
    backup(p)
    write(p, text, bom)
    print("저장 완료: billing.py")

print("\n완료. 아래 명령으로 변경 내용을 확인하세요: git diff")