import re
from pathlib import Path

p = Path("app/auth/repository.py")
raw = p.read_bytes()
bom = raw.startswith(b"\xef\xbb\xbf")
text = raw.decode("utf-8-sig")

pat = re.compile(
    r'(?P<i>[ \t]+)self\.add_onetime_credit\(user_id\)(?P<nl>\r?\n)(?P=i)return True'
)
if "DELETE FROM purchases WHERE id = ?" in text:
    print("SKIP: 이미 적용됨")
elif not pat.search(text):
    print("SKIP: 대상 코드를 찾지 못함 (repository.py 314~337행을 확인해 주세요)")
else:
    def repl(m):
        i, nl = m.group("i"), m.group("nl")
        return (
            f"{i}try:{nl}"
            f"{i}    self.add_onetime_credit(user_id){nl}"
            f"{i}except Exception:{nl}"
            f"{i}    # 크레딧 지급 실패 시 구매 기록을 되돌려 재시도가 가능하게 함{nl}"
            f'{i}    self._run("DELETE FROM purchases WHERE id = ?", (purchase_id,)){nl}'
            f"{i}    raise{nl}"
            f"{i}return True"
        )
    text = pat.sub(repl, text, count=1)
    p.write_bytes((b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8"))
    print("OK: repository.py 수정 완료")