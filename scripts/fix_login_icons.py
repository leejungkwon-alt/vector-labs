# scripts/fix_login_icons.py
from pathlib import Path
import sys

# 1. SocialLoginModal.tsx에서 깨진 Ionicons를 이모지로 교체
modal_path = Path("frontend/src/components/SocialLoginModal.tsx")
if modal_path.exists():
    src = modal_path.read_text(encoding="utf-8")
    
    # 구글 아이콘 교체
    src = src.replace(
        '<Ionicons name="logo-google" size={20} color="#000" />',
        '<Text style={{ fontSize: 20, marginRight: 8 }}>🌐</Text>'
    )
    # 카카오 아이콘 교체
    src = src.replace(
        '<Ionicons name="chatbubble" size={20} color="#000" />',
        '<Text style={{ fontSize: 20, marginRight: 8 }}>💬</Text>'
    )
    # 애플 아이콘 교체 (주석 처리되어 있지만 혹시 모르니)
    src = src.replace(
        '<Ionicons name="logo-apple" size={20} color={colors.onPrimary} />',
        '<Text style={{ fontSize: 20, marginRight: 8 }}>🍎</Text>'
    )
    
    modal_path.write_text(src, encoding="utf-8")
    print("✅ SocialLoginModal.tsx 아이콘을 이모지로 교체 완료")

# 2. settings.tsx 등 다른 곳의 깨진 아이콘 방지를 위해 expo-font 재설치 안내
print("\\n💡 아래 명령어를 실행하여 아이콘 폰트 패키지를 복구해주세요.")