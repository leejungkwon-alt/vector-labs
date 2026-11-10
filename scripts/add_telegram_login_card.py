# scripts/add_telegram_login_card.py
from pathlib import Path
import sys
import re

PATH = Path("frontend/app/(tabs)/settings.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 기존 "SNS 계정 연동하기" 블록을 찾아서, 텔레그램 환경일 때는 "텔레그램으로 로그인" 카드를 보여주도록 수정
old_block = '''      {/* ⭐️ 추가된 부분: 익명 로그인 상태일 때 계정 연결 유도 */}
      {user?.is_anonymous && !isTgEnv && (
        <View style={[styles.profileBox, { backgroundColor: colors.surface, borderColor: colors.primary }]}>
          <Text style={[styles.sectionTitle, { color: colors.primary }]}>{t("settings.linkAccountTitle")}</Text>
          <Text style={{ fontSize: 14, color: colors.text, marginBottom: 12, lineHeight: 20 }}>
            {t("settings.linkAccountDesc")}
          </Text>
          <TouchableOpacity style={styles.upgradeBtn} onPress={handleLinkAccount}>
            <Text style={styles.upgradeBtnText}>{t("settings.linkAccountCta")}</Text>
          </TouchableOpacity>
        </View>
      )}'''

new_block = '''      {/* ⭐️ 게스트 상태: 텔레그램 환경이면 텔레그램 로그인 카드, 아니면 SNS 연동 카드 */}
      {user?.is_anonymous && (
        isTgEnv ? (
          <View style={[styles.profileBox, { backgroundColor: "#f0f8ff", borderColor: "#0088cc" }]}>
            <Text style={[styles.sectionTitle, { color: "#0088cc" }]}>텔레그램으로 로그인</Text>
            <Text style={{ fontSize: 14, color: colors.text, marginBottom: 12, lineHeight: 20 }}>
              텔레그램 계정으로 로그인하면 모든 기기에서 프리미엄 혜택을 그대로 이용할 수 있습니다.
            </Text>
            <TouchableOpacity 
              style={[styles.upgradeBtn, { backgroundColor: "#0088cc" }]} 
              onPress={() => {
                useAuthStore.getState().loginWithTelegram().then(() => {
                  useAuthStore.getState().bootstrap();
                }).catch((e: any) => alert(e.message));
              }}
            >
              <Text style={styles.upgradeBtnText}>텔레그램으로 1초 만에 로그인</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <View style={[styles.profileBox, { backgroundColor: colors.surface, borderColor: colors.primary }]}>
            <Text style={[styles.sectionTitle, { color: colors.primary }]}>{t("settings.linkAccountTitle")}</Text>
            <Text style={{ fontSize: 14, color: colors.text, marginBottom: 12, lineHeight: 20 }}>
              {t("settings.linkAccountDesc")}
            </Text>
            <TouchableOpacity style={styles.upgradeBtn} onPress={handleLinkAccount}>
              <Text style={styles.upgradeBtnText}>{t("settings.linkAccountCta")}</Text>
            </TouchableOpacity>
          </View>
        )
      )}'''

if old_block in src:
    src = src.replace(old_block, new_block, 1)
    PATH.write_text(src, encoding="utf-8")
    print("✅ settings.tsx에 텔레그램 로그인 카드 추가 완료")
else:
    print("❌ 기존 블록을 찾지 못했습니다. 수동 확인 필요.")