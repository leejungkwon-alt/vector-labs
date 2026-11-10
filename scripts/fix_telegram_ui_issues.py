# scripts/fix_telegram_ui_issues.py
from pathlib import Path
import sys
import re

# ==========================================
# 1. SocialLoginModal.tsx: 네모 박스(깨진 아이콘) 제거
# ==========================================
modal_path = Path("frontend/src/components/SocialLoginModal.tsx")
if modal_path.exists():
    src = modal_path.read_text(encoding="utf-8")
    # 깨진 이모지(🔲)가 들어간 부분을 깔끔한 텍스트로 교체
    src = re.sub(r'<Text style=\{\{ fontSize: 20, marginRight: 8 \}\}>.*?</Text>', '', src)
    # 혹시 남아있을 수 있는 Ionicons paper-plane 제거
    src = src.replace('<Ionicons name="paper-plane" size={20} color="#FFF" />', '')
    modal_path.write_text(src, encoding="utf-8")
    print("✅ SocialLoginModal.tsx 깨진 아이콘 제거 완료")

# ==========================================
# 2. DateTimeField.tsx: 터치 씹힘 완벽 방지 (모달 닫힐 때 포커스 강제 해제)
# ==========================================
dt_path = Path("frontend/src/components/DateTimeField.tsx")
if dt_path.exists():
    src = dt_path.read_text(encoding="utf-8")
    
    # BirthDateWheelPicker의 onClose 시점에 포커스 해제 로직 추가
    old_close = 'onClose={() => setShowWheel(false)}'
    new_close = '''onClose={() => {
              setShowWheel(false);
              if (Platform.OS === "web" && typeof document !== "undefined" && document.activeElement instanceof HTMLElement) {
                document.activeElement.blur();
              }
            }}'''
    if old_close in src:
        src = src.replace(old_close, new_close, 1)
        print("✅ DateTimeField.tsx 모달 닫힘 시 포커스 해제 로직 추가 완료")
    else:
        print("⚠️ DateTimeField.tsx에서 onClose 패턴을 찾지 못했습니다.")

# ==========================================
# 3. settings.tsx: 로그인 후 상태 갱신 및 UI 즉시 반영
# ==========================================
settings_path = Path("frontend/app/(tabs)/settings.tsx")
if settings_path.exists():
    src = settings_path.read_text(encoding="utf-8")
    
    # SocialLoginModal의 onSuccess 콜백에서 유저 상태를 강제로 새로고침하도록 수정
    # (기존 onSuccess 로직을 찾아서 bootstrap 추가)
    old_success = '''        onSuccess={() => {
          setShowLogin(false);'''
    new_success = '''        onSuccess={async () => {
          await useAuthStore.getState().bootstrap(); // 유저 정보 강제 갱신
          setShowLogin(false);'''
    
    if old_success in src:
        src = src.replace(old_success, new_success, 1)
        settings_path.write_text(src, encoding="utf-8")
        print("✅ settings.tsx 로그인 성공 시 상태 강제 갱신(bootstrap) 추가 완료")
    else:
        print("⚠️ settings.tsx에서 onSuccess 패턴을 찾지 못했습니다.")