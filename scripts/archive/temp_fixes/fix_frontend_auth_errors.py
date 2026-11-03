# -*- coding: utf-8 -*-
"""
프론트엔드 401(토큰 만료) 에러 핸들링 스크립트
- 케미(compatibility): 401 에러 시 '세션 만료' 안내 및 홈 이동 버튼 노출
- 데일리(daily): 401 에러 시 안내 화면 노출 및 빈 화면(return null) 방지
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMPAT_FILE = ROOT / "frontend" / "app" / "(tabs)" / "compatibility.tsx"
DAILY_FILE = ROOT / "frontend" / "app" / "(tabs)" / "daily.tsx"

def patch_compatibility():
    if not COMPAT_FILE.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {COMPAT_FILE}")
        return

    text = COMPAT_FILE.read_text(encoding="utf-8")
    
    # 1. 기존 403 에러 처리 블록 찾기
    old_block = """      // 👇 403 에러(궁합 결제 필요)일 때 예쁜 결제 유도 화면 노출
      if (error instanceof ApiError && error.status === 403) {
        return (
          <View style={{ marginTop: 30, padding: 24, backgroundColor: colors.primary + "10", borderRadius: radius.lg, alignItems: "center", borderWidth: 1, borderColor: colors.primary + "30" }}>
            <Text style={{ fontSize: 40, marginBottom: 12 }}>💎</Text>
            <Text style={{ fontSize: 20, fontWeight: "800", color: colors.text, marginBottom: 8 }}>{t("compatibility.paywallTitle")}</Text>
            <Text style={{ fontSize: 15, color: colors.textMuted, textAlign: "center", marginBottom: 24, lineHeight: 22 }}>
              {t("compatibility.paywallBody")}
            </Text>
            <TouchableOpacity 
              style={{ backgroundColor: colors.primary, paddingHorizontal: 24, paddingVertical: 16, borderRadius: radius.md, width: "100%", alignItems: "center" }} 
              onPress={() => setShowPayment(true)}
            >
              <Text style={{ color: "#FFF", fontSize: 16, fontWeight: "700" }}>{t("compatibility.paywallCta")}</Text>
            </TouchableOpacity>
          </View>
        );
      }"""

    # 2. 401 및 403 통합 처리 블록
    new_block = """      // 👇 401(세션 만료) 또는 403(구독/결제 필요) 에러 핸들링
      const status = error instanceof ApiError ? error.status : 500;
      if (status === 401 || status === 403) {
        const isAuthError = status === 401;
        return (
          <View style={{ marginTop: 30, padding: 24, backgroundColor: colors.primary + "10", borderRadius: radius.lg, alignItems: "center", borderWidth: 1, borderColor: colors.primary + "30" }}>
            <Text style={{ fontSize: 40, marginBottom: 12 }}>{isAuthError ? "🔒" : "💎"}</Text>
            <Text style={{ fontSize: 20, fontWeight: "800", color: colors.text, marginBottom: 8 }}>
              {isAuthError ? "세션이 만료되었습니다" : t("compatibility.paywallTitle")}
            </Text>
            <Text style={{ fontSize: 15, color: colors.textMuted, textAlign: "center", marginBottom: 24, lineHeight: 22 }}>
              {isAuthError ? "앱을 다시 시작하거나 새로고침해 주세요." : t("compatibility.paywallBody")}
            </Text>
            <TouchableOpacity 
              style={{ backgroundColor: colors.primary, paddingHorizontal: 24, paddingVertical: 16, borderRadius: radius.md, width: "100%", alignItems: "center" }} 
              onPress={() => isAuthError ? router.replace("/") : setShowPayment(true)}
            >
              <Text style={{ color: "#FFF", fontSize: 16, fontWeight: "700" }}>
                {isAuthError ? "홈으로 돌아가기" : t("compatibility.paywallCta")}
              </Text>
            </TouchableOpacity>
          </View>
        );
      }"""

    if old_block in text:
        text = text.replace(old_block, new_block)
        COMPAT_FILE.write_text(text, encoding="utf-8")
        print("✅ compatibility.tsx: 401 에러 핸들링 추가 완료")
    else:
        print("⚠️ compatibility.tsx: 패치할 403 에러 블록을 찾지 못했습니다. (이미 수정되었거나 코드가 다름)")


def patch_daily():
    if not DAILY_FILE.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {DAILY_FILE}")
        return

    text = DAILY_FILE.read_text(encoding="utf-8")

    # 1. 에러 처리부 (401/403 통합)
    old_err = """  if (error) {
    const isForbidden = (error as any)?.status === 403;
    if (isForbidden) {
      return (
        <View style={styles.center}>
          <View style={{ backgroundColor: colors.surface, padding: 24, borderRadius: radius.lg, alignItems: "center", borderWidth: 1, borderColor: colors.border }}>
            <Ionicons name="lock-closed" size={48} color={colors.primary} style={{ marginBottom: 16 }} />
            <Text style={{ fontSize: 20, fontWeight: "700", color: colors.text, marginBottom: 8 }}>{t("daily.subscriberOnlyTitle")}</Text>
            <Text style={{ fontSize: 15, color: colors.textMuted, textAlign: "center", lineHeight: 22, marginBottom: 24 }}>
              {t("daily.subscriberOnlyBody")}
            </Text>
            <TouchableOpacity style={{ backgroundColor: colors.primary, paddingHorizontal: 24, paddingVertical: 14, borderRadius: radius.md, width: "100%", alignItems: "center" }} onPress={() => setShowPayment(true)}>
              <Text style={{ color: "#FFF", fontSize: 16, fontWeight: "700" }}>{t("daily.upgrade")}</Text>
            </TouchableOpacity>
          </View>
          <PaymentModal visible={showPayment} onClose={() => setShowPayment(false)} />
        </View>
      );
    }
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>{t("daily.errorTitle")}</Text>
        <Text style={styles.errorDetail}>{(error as Error).message}</Text>
      </View>
    );
  }"""

    new_err = """  if (error) {
    const status = (error as any)?.status;
    if (status === 401 || status === 403) {
      const isAuthError = status === 401;
      return (
        <View style={styles.center}>
          <View style={{ backgroundColor: colors.surface, padding: 24, borderRadius: radius.lg, alignItems: "center", borderWidth: 1, borderColor: colors.border }}>
            <Ionicons name="lock-closed" size={48} color={colors.primary} style={{ marginBottom: 16 }} />
            <Text style={{ fontSize: 20, fontWeight: "700", color: colors.text, marginBottom: 8 }}>
              {isAuthError ? "세션이 만료되었습니다" : t("daily.subscriberOnlyTitle")}
            </Text>
            <Text style={{ fontSize: 15, color: colors.textMuted, textAlign: "center", lineHeight: 22, marginBottom: 24 }}>
              {isAuthError ? "다시 로그인하거나 앱을 새로고침해 주세요." : t("daily.subscriberOnlyBody")}
            </Text>
            <TouchableOpacity style={{ backgroundColor: colors.primary, paddingHorizontal: 24, paddingVertical: 14, borderRadius: radius.md, width: "100%", alignItems: "center" }} onPress={() => isAuthError ? router.replace("/") : setShowPayment(true)}>
              <Text style={{ color: "#FFF", fontSize: 16, fontWeight: "700" }}>
                {isAuthError ? "홈으로 가기" : t("daily.upgrade")}
              </Text>
            </TouchableOpacity>
          </View>
          {!isAuthError && <PaymentModal visible={showPayment} onClose={() => setShowPayment(false)} />}
        </View>
      );
    }
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>{t("daily.errorTitle")}</Text>
        <Text style={styles.errorDetail}>{(error as Error).message}</Text>
      </View>
    );
  }"""
    
    # 2. 빈 화면(return null) 방지
    old_null = """  const dailyData = data?.daily as DailyResponse["daily"];
  if (!dailyData || !dailyData.items) return null;"""

    new_null = """  const dailyData = data?.daily as DailyResponse["daily"];
  if (!dailyData || !dailyData.items) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>{t("common.error")}</Text>
        <Text style={styles.errorDetail}>데이터를 불러올 수 없습니다. 잠시 후 다시 시도해 주세요.</Text>
      </View>
    );
  }"""

    changed = False
    if old_err in text:
        text = text.replace(old_err, new_err)
        changed = True
    if old_null in text:
        text = text.replace(old_null, new_null)
        changed = True

    if changed:
        DAILY_FILE.write_text(text, encoding="utf-8")
        print("✅ daily.tsx: 401 에러 핸들링 및 빈 화면 방지 완료")
    else:
        print("⚠️ daily.tsx: 패치할 블록을 찾지 못했습니다. (이미 수정되었거나 코드가 다름)")


if __name__ == "__main__":
    print("🚀 프론트엔드 인증 에러(401) 핸들링 패치 시작...")
    patch_compatibility()
    patch_daily()
    print("🎉 패치가 완료되었습니다. 프론트엔드(Expo)를 새로고침 해주세요.")