# scripts/debug_telegram_force.py
from pathlib import Path
import sys

PATH = Path("frontend/app/(tabs)/settings.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 기존 텔레그램 UI 조건문을 찾아서 무조건 보이는 디버그 박스로 교체
old_condition = '{isTgEnv && ('
new_condition = '''{true && (
        <View style={{ backgroundColor: "yellow", padding: 12, marginVertical: 8, borderRadius: 8 }}>
          <Text style={{ fontWeight: "bold", fontSize: 12 }}>DEBUG INFO:</Text>
          <Text style={{ fontSize: 11 }}>Telegram Object: {String(typeof window !== "undefined" && !!(window as any).Telegram)}</Text>
          <Text style={{ fontSize: 11 }}>WebApp Object: {String(typeof window !== "undefined" && !!(window as any).Telegram?.WebApp)}</Text>
          <Text style={{ fontSize: 11 }}>initData Length: {String(typeof window !== "undefined" ? (window as any).Telegram?.WebApp?.initData?.length || 0 : 0)}</Text>
        </View>
      )}
      {false && ('''

if old_condition in src:
    src = src.replace(old_condition, new_condition, 1)
    PATH.write_text(src, encoding="utf-8")
    print("✅ 디버그 박스 강제 노출 패치 완료")
else:
    print("⚠️ 대상 코드를 찾지 못했습니다. (이미 true로 변경되었을 수 있습니다.)")