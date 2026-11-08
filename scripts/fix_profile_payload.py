# scripts/fix_profile_payload.py
"""
1) 백엔드 ProfilePayload: extra="ignore" (여분 필드 무시)
2) 프론트 profileStore.saveProfile: 명시적 필드만 추출
"""
import ast
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

# ═══════════════════════════════════════════════════════════
# 1. 백엔드: ProfilePayload → extra="ignore"
# ═══════════════════════════════════════════════════════════
AUTH = Path("app/schemas/auth.py")
if AUTH.exists():
    atxt = AUTH.read_text(encoding="utf-8")
    
    OLD = '''class ProfilePayload(BaseModel):
    """PUT /me/profile — full replace."""

    model_config = ConfigDict(extra="forbid")'''
    
    NEW = '''class ProfilePayload(BaseModel):
    """PUT /me/profile — full replace."""

    # extra="ignore" (여분 필드 무시 — 프론트 호환성)
    model_config = ConfigDict(extra="ignore")'''
    
    if OLD in atxt:
        atxt = atxt.replace(OLD, NEW, 1)
        print("✅ 백엔드: ProfilePayload extra='forbid' → 'ignore'")
        try:
            ast.parse(atxt)
            if APPLY:
                AUTH.write_text(atxt, encoding="utf-8")
        except SyntaxError as e:
            print(f"❌ 문법 오류: {e.lineno}")
            sys.exit(1)
    elif 'extra="ignore"' in atxt and "ProfilePayload" in atxt:
        print("ℹ️ 백엔드: 이미 패치됨")
    else:
        print("⚠️ 백엔드 ProfilePayload 패턴 불일치")

# ═══════════════════════════════════════════════════════════
# 2. 프론트: saveProfile에서 명시적 필드만 전송
# ═══════════════════════════════════════════════════════════
STORE = Path("frontend/src/store/profileStore.ts")
if STORE.exists():
    stxt = STORE.read_text(encoding="utf-8")
    
    # saveProfile 함수에 명시적 필드 추출 + 백엔드 PUT 호출 삽입
    OLD_SAVE = '''    saveProfile: async (profile: any) => {
      // 1. 로컬 저장 (오프라인/새로고침 대비)
      await AsyncStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
      set({ profile });'''
    
    NEW_SAVE = '''    saveProfile: async (profile: any) => {
      // 1. 로컬 저장 (오프라인/새로고침 대비)
      await AsyncStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
      set({ profile });
      // 2. 백엔드 PUT (extra 필드 방지: 명시적 필드만)
      try {
        const payload: any = {
          birth_date: profile.birth_date ?? null,
          birth_time: profile.birth_time ?? null,
          birth_location: profile.birth_location ?? null,
          timezone_str: profile.timezone_str || "Asia/Seoul",
          longitude: typeof profile.longitude === "number" ? profile.longitude : 126.978,
          gender: profile.gender || "M",
          jasi_boundary: typeof profile.jasi_boundary === "number" ? profile.jasi_boundary : 23,
          correction_mode: profile.correction_mode || "lmt",
        };
        await api.updateProfile(payload);
      } catch (e) {
        console.warn("[saveProfile] backend sync failed:", e);
        throw e;
      }'''
    
    if OLD_SAVE in stxt:
        stxt = stxt.replace(OLD_SAVE, NEW_SAVE, 1)
        print("✅ 프론트: saveProfile에 명시적 필드 PUT 추가")
        if APPLY:
            STORE.write_text(stxt, encoding="utf-8")
    elif "extra 필드 방지" in stxt:
        print("ℹ️ 프론트: 이미 패치됨")
    else:
        print("⚠️ 프론트 saveProfile 패턴 불일치")
        print("   다음 명령으로 확인:")
        print("   Get-Content 'frontend/src/store/profileStore.ts' | Select-String 'saveProfile' -Context 0,10")

print()
if not APPLY:
    print("🧪 미리보기. 적용: python scripts/fix_profile_payload.py --apply")
else:
    print("🎉 완료. 다음:")
    print("   .\\deploy.ps1  (백엔드 재배포)")
    print('   git add "frontend/src/store/profileStore.ts"')
    print('   git commit -m "fix(profile): explicit PUT payload + extra ignore"')
    print("   git push origin main")