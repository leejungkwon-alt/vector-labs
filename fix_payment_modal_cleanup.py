# fix_payment_modal_cleanup.py
from pathlib import Path
import re, shutil
from datetime import datetime

T = Path("frontend/src/components/PaymentModal.tsx")
src = T.read_text(encoding="utf-8")

# line 22 이후, if(window) 블록 전체 제거하고 그 앞에 invalidate+bootstrap 통합
old_block = re.compile(
    r"(await api\.purchase\(productId\);\s*\n)"
    r"\s*await bootstrap\(\);[^\n]*\n"
    r"\s*Alert\.alert\([^\n]+\);\n"
    r"\s*onClose\(\);\n"
    r"\s*if\s*\(typeof window !== \"undefined\"\)\s*\{.*?\n\s*\}\n",
    re.DOTALL,
)
new_block = (
    r"\1"
    "      try { await queryClient.invalidateQueries(); } "
    "catch (e) { console.warn('[FIX-21] cache invalidate failed', e); }\n"
    "      await bootstrap();\n"
    "      Alert.alert(\"Payment Successful\", \"The locked content has been unlocked.\");\n"
    "      onClose();\n"
)
new, n = old_block.subn(new_block, src)
if n == 0:
    print("[SKIP] 패턴 매치 없음 - 수동 정리 권장"); exit(1)
try:
    compile(new, str(T), "exec")  # py 문법 검증은 의미 없지만 안전성
except: pass

bak = T.with_suffix(T.suffix + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S"))
shutil.copy2(T, bak)
T.write_text(new, encoding="utf-8")
print(f"[OK] PaymentModal 정리 (백업: {bak.name})")