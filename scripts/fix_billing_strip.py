import re
from pathlib import Path

p = Path("app/api/v1/endpoints/billing.py")
raw = p.read_bytes()
text = raw.decode("utf-8-sig")
bom = raw.startswith(b"\xef\xbb\xbf")
orig = text

for name in ("LEMONSQUEEZY_ONETIME_VARIANT_ID", "LEMONSQUEEZY_WEBHOOK_SECRET"):
    pat = re.compile(r'os\.environ\.get\("%s",\s*""\)(?!\.strip)' % name)
    text, n = pat.subn('os.environ.get("%s", "").strip()' % name, text)
    print(f"{name}: {n}곳 수정")

if text != orig:
    p.write_bytes((b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8"))
    print("저장 완료")
else:
    print("변경 없음 (이미 적용됨)")