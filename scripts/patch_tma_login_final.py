# scripts/patch_tma_login_final.py
from pathlib import Path
import sys
import re

# ==========================================
# 1. 백엔드 (app/auth/router.py) 패치
# ==========================================
backend_path = Path("app/auth/router.py")
if backend_path.exists():
    src = backend_path.read_text(encoding="utf-8")
    if "/login/telegram" not in src:
        # 텔레그램 검증 모듈 import 추가
        import_stmt = '''
from app.api.v1.endpoints.telegram import _verified_telegram_id, TelegramInitData
'''
        if "from app.api.v1.endpoints.telegram import" not in src:
            # 파일 상단의 첫 번째 from app... 문 뒤에 추가
            src = re.sub(r'(from app\.auth\.repository import[^\n]+\n)', r'\1' + import_stmt, src, count=1)

        # 로그인 엔드포인트 추가
        endpoint = '''

@router.post("/login/telegram")
def login_telegram(payload: TelegramInitData):
    from app.auth.security import create_access_token
    from app.auth.repository import get_repository
    
    tg_id = _verified_telegram_id(payload)
    repo = get_repository()
    
    # 텔레그램 ID로 기존 유저 찾기 (없으면 생성)
    user = None
    try:
        # 기존 레포지토리에 텔레그램 ID로 유저를 찾는 함수가 있다고 가정
        user = repo.get_user_by_telegram_id(tg_id)
    except AttributeError:
        pass
        
    if not user:
        # 없으면 새 계정 생성 (익명 계정과 동일하게 처리)
        user = repo.create_anonymous_user()
        # 텔레그램 구독자로 등록 (ID 연동)
        repo.upsert_telegram_subscriber(tg_id, user["id"], payload.lang or "ko")
    
    # JWT 토큰 발급
    token = create_access_token({"sub": user["id"]})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }
'''
        src += endpoint
        backend_path.write_text(src, encoding="utf-8")
        print("✅ 백엔드 app/auth/router.py 패치 완료")
    else:
        print("⚠️ 백엔드에 이미 텔레그램 로그인 엔드포인트가 있습니다.")
else:
    print("❌ app/auth/router.py 파일을 찾을 수 없습니다.")


# ==========================================
# 2. 프론트엔드 (api/client.ts) 패치
# ==========================================
client_path = Path("frontend/src/api/client.ts")
if client_path.exists():
    src = client_path.read_text(encoding="utf-8")
    if "loginTelegram" not in src:
        src = src.replace(
            'loginProvider: (provider: string, token: string) => request<AuthResponse>(`/auth/login/${provider}`, { method: "POST", body: JSON.stringify({ provider_token: token }) }),',
            'loginProvider: (provider: string, token: string) => request<AuthResponse>(`/auth/login/${provider}`, { method: "POST", body: JSON.stringify({ provider_token: token }) }),\n  loginTelegram: (initData: string) => request<AuthResponse>("/auth/login/telegram", { method: "POST", body: JSON.stringify({ init_data: initData }) }),'
        )
        client_path.write_text(src, encoding="utf-8")
        print("✅ 프론트엔드 api/client.ts 패치 완료")


# ==========================================
# 3. 프론트엔드 (store/authStore.ts) 패치
# ==========================================
store_path = Path("frontend/src/store/authStore.ts")
if store_path.exists():
    src = store_path.read_text(encoding="utf-8")
    if "loginWithTelegram" not in src:
        # 상태 인터페이스 추가
        src = src.replace(
            "signInWithProvider: (provider: Provider) => Promise<void>;",
            "signInWithProvider: (provider: Provider) => Promise<void>;\n  loginWithTelegram: () => Promise<void>;"
        )
        # 액션 추가
        action = '''
  loginWithTelegram: async () => {
    const tg = (window as any).Telegram?.WebApp;
    if (!tg || !tg.initData) throw new Error("Telegram environment not found");
    
    const res = await api.loginTelegram(tg.initData);
    await storage.setItem(TOKEN_KEY, res.access_token);
    setAuthToken(res.access_token);
    set({ user: res.user, ready: true });
    try { await useProfileStore.getState().loadProfile(); } catch {}
  },
'''
        src = src.replace("signInWithProvider: async (provider: Provider) => {", action + "  signInWithProvider: async (provider: Provider) => {", 1)
        store_path.write_text(src, encoding="utf-8")
        print("✅ 프론트엔드 store/authStore.ts 패치 완료")


# ==========================================
# 4. 프론트엔드 (components/SocialLoginModal.tsx) 패치
# ==========================================
modal_path = Path("frontend/src/components/SocialLoginModal.tsx")
if modal_path.exists():
    src = modal_path.read_text(encoding="utf-8")
    if "isTelegram" not in src:
        # 4-1. useEffect import 추가
        src = src.replace('import React, { useState } from "react";', 'import React, { useState, useEffect } from "react";')
        
        # 4-2. isTelegram 상태 추가
        src = src.replace(
            'const [mode, setMode] = useState<"link" | "login">("login");',
            'const [mode, setMode] = useState<"link" | "login">("login");\n  const [isTelegram, setIsTelegram] = useState(false);\n  useEffect(() => { setIsTelegram(!!(window as any).Telegram?.WebApp?.initData); }, []);'
        )
        
        # 4-3. handleTelegramLogin 함수 추가
        src = src.replace(
            'const handleLogin = async (provider: "apple" | "google" | "kakao") => {',
            'const handleTelegramLogin = async () => {\n    setLoading("telegram");\n    try {\n      await useAuthStore.getState().loginWithTelegram();\n      onSuccess();\n    } catch (e: any) {\n      alert(e.message || "로그인 실패");\n    } finally {\n      setLoading(null);\n    }\n  };\n\n  const handleLogin = async (provider: "apple" | "google" | "kakao") => {'
        )
        
        # 4-4. UI 조건부 렌더링 (구글/카카오 버튼 숨기고 텔레그램 버튼 보이기)
        google_btn = '''<TouchableOpacity style={[styles.btn, styles.googleBtn]} onPress={() => handleLogin("google")} disabled={!!loading}>
            {loading === "google" ? <ActivityIndicator color="#000" /> : (
              <>
                <Ionicons name="logo-google" size={20} color="#000" />
                <Text style={styles.btnTextBlack}>{mode === "login" ? t("socialLogin.googleLoginCta") : t("socialLogin.googleCta")}</Text>
              </>
            )}
          </TouchableOpacity>'''
        src = src.replace(google_btn, '{!isTelegram && (' + google_btn + ')}')

        kakao_btn = '''<TouchableOpacity style={[styles.btn, styles.kakaoBtn]} onPress={() => handleLogin("kakao")} disabled={!!loading}>
            {loading === "kakao" ? <ActivityIndicator color="#000" /> : (
              <>
                <Ionicons name="chatbubble" size={20} color="#000" />
                <Text style={styles.btnTextBlack}>{mode === "login" ? t("socialLogin.kakaoLoginCta") : t("socialLogin.kakaoCta")}</Text>
              </>
            )}
          </TouchableOpacity>'''
        src = src.replace(kakao_btn, '{!isTelegram && (' + kakao_btn + ')}\n\n          {isTelegram && (\n            <TouchableOpacity style={[styles.btn, { backgroundColor: "#0088cc" }]} onPress={handleTelegramLogin} disabled={!!loading}>\n              {loading === "telegram" ? <ActivityIndicator color="#FFF" /> : (\n                <>\n                  <Ionicons name="paper-plane" size={20} color="#FFF" />\n                  <Text style={styles.btnTextWhite}>텔레그램으로 1초 만에 로그인</Text>\n                </>\n              )}\n            </TouchableOpacity>\n          )}')

        # 4-5. 구분선(or) 및 하단 토글 숨기기 (텔레그램에서는 불필요)
        src = src.replace('<View style={styles.divider}>', '{!isTelegram && <View style={styles.divider}>')
        src = src.replace('</View>\n\n          <TouchableOpacity\n            style={styles.modeToggle}', '</View>}\n\n          {!isTelegram && <TouchableOpacity\n            style={styles.modeToggle}')
        src = src.replace('disabled={!!loading}\n          >\n\n          <Text style={styles.modeToggleText}>', 'disabled={!!loading}\n          >\n\n          <Text style={styles.modeToggleText}>')
        src = src.replace('</TouchableOpacity>\n\n          <TouchableOpacity style={styles.closeBtn}', '</TouchableOpacity>}\n\n          <TouchableOpacity style={styles.closeBtn}')

        modal_path.write_text(src, encoding="utf-8")
        print("✅ 프론트엔드 SocialLoginModal.tsx 패치 완료")