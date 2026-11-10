# scripts/patch_compat_share.py
from pathlib import Path
import sys
import difflib

PATH = Path("frontend/app/(tabs)/compatibility.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 1. Import 추가
old_imports = 'import { useState } from "react";\nimport { useQuery } from "@tanstack/react-query";\nimport { View, Text, ScrollView, TouchableOpacity, StyleSheet, ActivityIndicator, Switch } from "react-native";'
new_imports = 'import { useState, useRef } from "react";\nimport { useQuery } from "@tanstack/react-query";\nimport { View, Text, ScrollView, TouchableOpacity, StyleSheet, ActivityIndicator, Switch, Platform } from "react-native";\nimport { captureRef } from "react-native-view-shot";\nimport * as Sharing from "expo-sharing";\nimport { Ionicons } from "@expo/vector-icons";'

if new_imports not in src:
    if old_imports not in src:
        print("❌ Import 부분 못 찾음"); sys.exit(1)
    src = src.replace(old_imports, new_imports, 1)

# 2. useRef 생성 및 handleShare 함수 추가
old_hook = '  const lang = useLanguageStore((s) => s.lang);'
new_hook = '''  const lang = useLanguageStore((s) => s.lang);
  const shareRef = useRef<View>(null);

  const handleShare = async () => {
    try {
      if (!shareRef.current) return;
      const uri = await captureRef(shareRef, { format: "png", quality: 1 });
      
      if (Platform.OS === "web") {
        // 웹: 다운로드
        const link = document.createElement("a");
        link.href = uri;
        link.download = "gyeol-compatibility.png";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        // 모바일: 네이티브 공유 시트
        if (await Sharing.isAvailableAsync()) {
          await Sharing.shareAsync(uri, { dialogTitle: "Share your Compatibility" });
        }
      }
    } catch (err) {
      console.error("Share failed:", err);
      alert("공유에 실패했습니다.");
    }
  };
'''
if new_hook not in src:
    if old_hook not in src:
        print("❌ lang hook 부분 못 찾음"); sys.exit(1)
    src = src.replace(old_hook, new_hook, 1)

# 3. 렌더링 영역 감싸기 (시작 지점)
old_render_start = '    return (\n      <View style={{ marginTop: 30, gap: 16 }}>\n        <View style={styles.resultCard}>'
new_render_start = '    return (\n      <View style={{ marginTop: 30 }}>\n        <View ref={shareRef} collapsable={false} style={{ gap: 16, paddingBottom: 20, backgroundColor: colors.bg }}>\n        <View style={styles.resultCard}>'

if new_render_start not in src:
    if old_render_start not in src:
        print("❌ renderResult 시작 부분 못 찾음"); sys.exit(1)
    src = src.replace(old_render_start, new_render_start, 1)

# 4. 렌더링 영역 닫기 및 공유 버튼/워터마크 추가 (끝 지점)
# 기존 map의 닫힘 태그를 찾아서 그 뒤에 워터마크와 공유 버튼을 넣습니다.
# (주의: 렌더링 끝부분은 `})}\n      </View>\n    );\n  };` 형태일 것임)
old_render_end = '        })}\n      </View>\n    );\n  };'
new_render_end = '''        })}
        
        {/* 워터마크 */}
        <Text style={{ textAlign: "center", fontSize: 12, color: colors.textMuted, marginTop: 10, fontWeight: "600" }}>
          Gyeol - gyeol-blond.vercel.app
        </Text>
        </View>

        {/* 공유 버튼 */}
        <TouchableOpacity 
          onPress={handleShare} 
          style={{ flexDirection: "row", justifyContent: "center", alignItems: "center", backgroundColor: colors.primary, padding: 16, borderRadius: radius.md, marginTop: 20 }}
        >
          <Ionicons name="share-outline" size={20} color="#FFF" style={{ marginRight: 8 }} />
          <Text style={{ color: "#FFF", fontSize: 16, fontWeight: "700" }}>
            {t("compatibility.share") || "Share"}
          </Text>
        </TouchableOpacity>
      </View>
    );
  };'''

if new_render_end not in src:
    if old_render_end not in src:
        print("❌ renderResult 끝 부분 못 찾음. 수동 확인 필요."); sys.exit(1)
    src = src.replace(old_render_end, new_render_end, 1)

# 5. Diff 미리보기
sys.stdout.writelines(difflib.unified_diff(
    PATH.read_text(encoding="utf-8").splitlines(keepends=True),
    src.splitlines(keepends=True),
    fromfile="before", tofile="after", n=2,
))

if "--apply" not in sys.argv:
    print("\n💡 dry-run. 적용: python scripts/patch_compat_share.py --apply")
    sys.exit(0)

PATH.write_text(src, encoding="utf-8")
print("\n✅ compatibility.tsx 공유 기능 패치 완료")