# scripts/fix_broken_icons.py
from pathlib import Path
import sys
import re

PATH = Path("frontend/src/components/PaymentModal.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 1. 닫기 버튼 (X 아이콘) -> 텍스트 ✕ 로 교체
src = src.replace(
    '<Ionicons name="close" size={24} color={colors.textMuted} />',
    '<Text style={{ fontSize: 22, color: colors.textMuted, lineHeight: 24 }}>✕</Text>'
)

# 2. 프리미엄 화살표 (chevron-forward) -> 텍스트 › 로 교체 (파란색)
src = src.replace(
    '<Ionicons name="chevron-forward" size={24} color={colors.primary} />',
    '<Text style={{ fontSize: 26, color: colors.primary, lineHeight: 26 }}>›</Text>'
)

# 3. 일시불 화살표 (chevron-forward) -> 텍스트 › 로 교체 (회색)
src = src.replace(
    '<Ionicons name="chevron-forward" size={24} color={colors.textMuted} />',
    '<Text style={{ fontSize: 26, color: colors.textMuted, lineHeight: 26 }}>›</Text>'
)

# 4. 혹시 남아있는 다른 Ionicons도 모두 안전한 텍스트로 대체
src = re.sub(
    r'<Ionicons name="([^"]+)"[^/]*/>',
    '<Text style={{ fontSize: 20 }}>•</Text>',
    src
)

# 5. Ionicons import 제거 (더 이상 사용하지 않으므로)
src = src.replace('import { Ionicons } from "@expo/vector-icons";\n', '')

PATH.write_text(src, encoding="utf-8")
print("✅ PaymentModal.tsx의 깨진 아이콘을 텍스트로 교체 완료")