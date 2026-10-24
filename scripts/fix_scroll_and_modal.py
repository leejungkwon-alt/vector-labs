import shutil
from pathlib import Path
from datetime import datetime

# ====================================================
# 1. Settings 화면 스크롤(ScrollView) 적용
# ====================================================
settings_file = Path("frontend/app/(tabs)/settings.tsx")

if settings_file.exists():
    src = settings_file.read_text(encoding="utf-8")
    
    # 1) import에 ScrollView 추가
    if "ScrollView" not in src:
        src = src.replace(
            'import { View, Text, TouchableOpacity, StyleSheet, Alert, Platform, Linking } from "react-native";',
            'import { View, Text, TouchableOpacity, StyleSheet, Alert, Platform, Linking, ScrollView } from "react-native";'
        )
        # 다른 형태의 import일 경우 대비
        if "ScrollView" not in src:
            src = src.replace(
                'import { View, Text, TouchableOpacity, StyleSheet, Alert, Platform } from "react-native";',
                'import { View, Text, TouchableOpacity, StyleSheet, Alert, Platform, ScrollView } from "react-native";'
            )

    # 2) 최상위 <View>를 <ScrollView>로 변경
    src = src.replace(
        "  return (\n    <View style={styles.container}>",
        "  return (\n    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 40 }}>"
    )
    # 3) 닫는 </View>를 </ScrollView>로 변경 (마지막 부분만)
    # 정규식을 사용해 가장 마지막의 </View>\n  );\n} 를 찾아 바꿉니다.
    if "</ScrollView>" not in src:
        src = src.replace("    </View>\n  );\n}", "    </ScrollView>\n  );\n}")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(settings_file, settings_file.with_suffix(f".tsx.bak.{ts}"))
    settings_file.write_text(src, encoding="utf-8")
    print("✅ 1. Settings 화면 스크롤(ScrollView) 적용 완료")
else:
    print("❌ settings.tsx 파일을 찾을 수 없습니다.")


# ====================================================
# 2. Compatibility 화면에 PaymentModal 직접 연결
# ====================================================
compat_file = Path("frontend/app/(tabs)/compatibility.tsx")

if compat_file.exists():
    src = compat_file.read_text(encoding="utf-8")

    # 1) PaymentModal import 추가
    if "PaymentModal" not in src:
        src = src.replace(
            'import { TimezonePickerModal } from "@/components/TimezonePickerModal";',
            'import { TimezonePickerModal } from "@/components/TimezonePickerModal";\nimport { PaymentModal } from "@/components/PaymentModal";'
        )

    # 2) showPayment 상태 추가
    if "const [showPayment, setShowPayment] = useState(false);" not in src:
        src = src.replace(
            '  const [showLogin, setShowLogin] = useState(false);', # (없을 수도 있음)
            '  const [showLogin, setShowLogin] = useState(false);\n  const [showPayment, setShowPayment] = useState(false);'
        )
        # 상태 추가 위치가 다를 경우 대비 (관계 유형 상태 아래)
        if "showPayment" not in src:
            src = src.replace(
                '  const [relationshipType, setRelationshipType] = useState<"romance" | "business" | "friend" | "family">("romance");',
                '  const [relationshipType, setRelationshipType] = useState<"romance" | "business" | "friend" | "family">("romance");\n  const [showPayment, setShowPayment] = useState(false);'
            )

    # 3) 403 에러 버튼의 onPress를 모달 띄우기로 변경
    src = src.replace(
        'onPress={() => router.push("/(tabs)/settings")}',
        'onPress={() => setShowPayment(true)}'
    )

    # 4) 컴포넌트 최하단(return문 안)에 PaymentModal 추가
    # CityPickerModal 등이 있는 부분 근처에 추가
    if "<PaymentModal" not in src:
        # 마지막 모달들 (CityPickerModal, TimezonePickerModal) 아래에 추가
        src = src.replace(
            '<TimezonePickerModal visible={showTimezoneModal} onClose={() => setShowTimezoneModal(false)} onSelect={setCustomTimezone} currentTz={customTimezone} />',
            '<TimezonePickerModal visible={showTimezoneModal} onClose={() => setShowTimezoneModal(false)} onSelect={setCustomTimezone} currentTz={customTimezone} />\n      <PaymentModal visible={showPayment} onClose={() => setShowPayment(false)} />'
        )
    
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(compat_file, compat_file.with_suffix(f".tsx.bak.{ts}"))
    compat_file.write_text(src, encoding="utf-8")
    print("✅ 2. Compatibility 화면 결제 모달 연동 완료")
else:
    print("❌ compatibility.tsx 파일을 찾을 수 없습니다.")

print("\n🚀 서버(Expo)를 재시작하고 화면을 새로고침 해보세요!")
