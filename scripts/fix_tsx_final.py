# scripts/fix_tsx_final.py
from pathlib import Path
import sys
import re

PATH = Path("frontend/app/(tabs)/settings.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 1. 중복된 useEffect import 수정
src = src.replace("import { useState, useEffect, useEffect } from 'react';", "import { useState, useEffect } from 'react';")
src = src.replace('import { useState, useEffect, useEffect } from "react";', 'import { useState, useEffect } from "react";')

# 2. 기존에 있던 텔레그램 관련 쓰레기 코드(디버그 박스, 깨진 UI) 전부 제거
# 주석 단위로 지우기 (텔레그램 알림 스위치 주석부터 시작하는 덩어리)
src = re.sub(r'\{/\* 텔레그램 알림 스위치.*?\}\)\}', '', src, flags=re.DOTALL)
src = re.sub(r'\{/\* 디버그용 빌드 마커.*?\}\)\}', '', src, flags=re.DOTALL)
# 만약 true && 로 시작하는 디버그 블록이 남아있다면 강제 제거
src = re.sub(r'\{true && \(\s*<View style=\{\{ backgroundColor: "yellow".*?</View>\s*\)\}', '', src, flags=re.DOTALL)

# 3. 언어 설정(Language) 파트를 찾아서 그 바로 위에 스위치 UI 삽입
anchor = '<Text style={styles.sectionTitle}>{t("settings.language") || "Language"}</Text>'
# 만약 위 anchor가 없다면, 안전하게 '언어 설정 (Language)' 텍스트를 찾음
if anchor not in src:
    anchor = '언어 설정 (Language)'
    if anchor not in src:
        anchor = '{t("settings.language")' # 그나마 가장 흔한 패턴

telegram_ui = '''      {/* 텔레그램 알림 스위치 */}
      {isTgEnv && (
        <View style={[styles.profileBox, { backgroundColor: "#f0f8ff", borderColor: "#0088cc" }]}>
          <Text style={{ fontSize: 10, color: "#aaa", marginBottom: 4 }}>BUILD 1110-B (Telegram Ready)</Text>
          <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
            <View style={{ flex: 1, marginRight: 10 }}>
              <Text style={{ fontSize: 16, fontWeight: "700", color: colors.text }}>텔레그램 알림 받기</Text>
              <Text style={{ fontSize: 12, color: colors.textMuted, marginTop: 4 }}>
                매일 아침 텔레그램으로 오늘의 운세를 보내드립니다.
              </Text>
            </View>
            <Switch 
              value={isTgSubscribed} 
              onValueChange={handleTelegramToggle} 
              disabled={isTgLoading} 
            />
          </View>
        </View>
      )}

'''

# 삽입 위치 찾기
if '언어 설정 (Language)' in src and '텔레그램 알림 스위치' not in src:
    src = src.replace('언어 설정 (Language)', telegram_ui + '언어 설정 (Language)', 1)
elif '<Text style={styles.sectionTitle}>{t("settings.language")' in src and '텔레그램 알림 스위치' not in src:
    src = src.replace('<Text style={styles.sectionTitle}>{t("settings.language")', telegram_ui + '<Text style={styles.sectionTitle}>{t("settings.language")', 1)
else:
    print("⚠️ UI 삽입 위치(언어 설정)를 찾지 못했습니다. 코드를 확인해주세요.")

PATH.write_text(src, encoding="utf-8")
print("✅ 중복 import 수정 및 UI 강제 삽입 완료")