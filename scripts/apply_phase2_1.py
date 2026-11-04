import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUFFIX = f".bak_phase2_1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# 1. PoemFlipCard.tsx (이미지 레이어 추가)
FLIP_CARD_TSX = '''import { useRef, useState } from "react";
import { View, Text, Pressable, Animated, StyleSheet, Alert, Platform, Image } from "react-native";
import { colors } from "@/theme";
import type { PoemCard } from "../../../types";

const FACE_HEIGHT = 480;
const USE_NATIVE = Platform.OS !== "web";

const C = {
  bg: (colors as any).bg || (colors as any).card || "#FBF8F2",
  border: (colors as any).border || "#E5DDD0",
  text: (colors as any).text || "#2A2620",
  muted: (colors as any).muted || "#8A8378",
  accent: (colors as any).accent || (colors as any).primary || "#B8860B",
  accentSoft: (colors as any).accentSoft || (colors as any).primarySoft || "#F5EBD8",
};

function tt(lang: string | undefined, ko: string, en: string): string {
  return lang === "ko" ? ko : en;
}

export function PoemFlipCard({
  poem,
  lang,
  onSubscribePress,
}: {
  poem: PoemCard;
  lang?: string;
  onSubscribePress?: () => void;
}) {
  const [flipped, setFlipped] = useState(false);
  const anim = useRef(new Animated.Value(0)).current;

  const flip = () => {
    Animated.timing(anim, {
      toValue: flipped ? 0 : 1,
      duration: 420,
      useNativeDriver: USE_NATIVE,
    }).start();
    setFlipped(!flipped);
  };

  const frontRotate = anim.interpolate({ inputRange: [0, 1], outputRange: ["0deg", "180deg"] });
  const backRotate  = anim.interpolate({ inputRange: [0, 1], outputRange: ["180deg", "360deg"] });
  const frontOpacity = anim.interpolate({ inputRange: [0, 0.5, 0.5, 1], outputRange: [1, 1, 0, 0] });
  const backOpacity  = anim.interpolate({ inputRange: [0, 0.5, 0.5, 1], outputRange: [0, 0, 1, 1] });

  const isWallpaperLocked = (poem.locked_fields || []).includes("wallpaper_image");

  const onSaveWallpaper = () => {
    if (isWallpaperLocked) { onSubscribePress?.(); return; }
    Alert.alert(
      tt(lang, "배경화면 저장", "Save wallpaper"),
      tt(lang, "배경화면 저장은 곧 지원됩니다.", "Wallpaper saving is coming soon."),
    );
  };

  // 임시 이미지 URL (실제 이미지 에셋이 준비되면 poem.calligraphy_image 사용)
  const imgUrl = "https://placehold.co/600x300/F5EBD8/B8860B.png?text=Calligraphy+Image";

  return (
    <View style={{ marginVertical: 16 }}>
      <Text style={styles.caption}>
        {tt(lang, "오늘의 시조", "Poem of the Day")} · {poem.relation_kr}
      </Text>

      <Pressable onPress={flip} accessibilityRole="button">
        <View style={{ height: FACE_HEIGHT, position: "relative" }}>
          <Animated.View
            pointerEvents={flipped ? "none" : "auto"}
            style={[StyleSheet.absoluteFillObject, styles.face,
                    { opacity: frontOpacity, transform: [{ perspective: 900 }, { rotateY: frontRotate }] }]}
          >
            <Image source={{ uri: imgUrl }} style={styles.image} resizeMode="cover" />
            <Text style={styles.elementBadge}>{poem.element}</Text>
            <Text style={styles.sijoText}>{poem.sijo_ko}</Text>
            {poem.keywords && poem.keywords.length > 0 && (
              <View style={styles.keywordRow}>
                {poem.keywords.map((k, i) => (
                  <Text key={i} style={styles.keyword}>#{k}</Text>
                ))}
              </View>
            )}
            <Text style={styles.tapHint}>{tt(lang, "탭하여 뒤집기 →", "Tap to flip →")}</Text>
          </Animated.View>

          <Animated.View
            pointerEvents={flipped ? "auto" : "none"}
            style={[StyleSheet.absoluteFillObject, styles.face,
                    { opacity: backOpacity, transform: [{ perspective: 900 }, { rotateY: backRotate }] }]}
          >
            <Text style={styles.title}>{poem.title}</Text>
            <Text style={styles.romanization}>{poem.romanization}</Text>
            <View style={styles.divider} />
            <Text style={styles.interpretation}>{poem.interpretation}</Text>
            {poem.practice ? (
              <View style={styles.practiceBox}>
                <Text style={styles.practiceLabel}>{tt(lang, "오늘의 실천", "Today's Practice")}</Text>
                <Text style={styles.practiceText}>{poem.practice}</Text>
              </View>
            ) : null}
            <Pressable onPress={onSaveWallpaper} style={styles.saveButton}>
              <Text style={styles.saveButtonText}>
                {isWallpaperLocked ? tt(lang, "배경화면 · 프리미엄", "Wallpaper · Premium") : tt(lang, "배경화면 저장", "Save wallpaper")}
              </Text>
            </Pressable>
            <Text style={styles.tapHint}>{tt(lang, "← 탭하여 돌아가기", "← Tap to flip back")}</Text>
          </Animated.View>
        </View>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  caption: { fontSize: 11, letterSpacing: 2, textTransform: "uppercase", color: C.muted, textAlign: "center", marginBottom: 8 },
  face: { backgroundColor: C.bg, borderRadius: 20, padding: 24, borderWidth: 1, borderColor: C.border, justifyContent: "center", shadowColor: "#000", shadowOpacity: 0.08, shadowRadius: 12, shadowOffset: { width: 0, height: 4 } },
  image: { width: "100%", height: 120, borderRadius: 12, marginBottom: 16, opacity: 0.9 },
  elementBadge: { fontSize: 36, textAlign: "center", marginBottom: 12, color: C.accent, fontWeight: "200" },
  sijoText: { fontSize: 20, lineHeight: 34, textAlign: "center", color: C.text, marginBottom: 20, fontWeight: "300" },
  keywordRow: { flexDirection: "row", flexWrap: "wrap", justifyContent: "center", gap: 6, marginBottom: 16 },
  keyword: { fontSize: 12, color: C.muted, paddingHorizontal: 8, paddingVertical: 4, borderWidth: 1, borderColor: C.border, borderRadius: 999 },
  title: { fontSize: 22, fontWeight: "600", textAlign: "center", color: C.text, marginBottom: 8 },
  romanization: { fontSize: 12, fontStyle: "italic", textAlign: "center", color: C.muted, marginBottom: 12 },
  divider: { height: 1, backgroundColor: C.border, marginVertical: 12 },
  interpretation: { fontSize: 15, lineHeight: 24, color: C.text, marginBottom: 16 },
  practiceBox: { backgroundColor: C.accentSoft, padding: 12, borderRadius: 12, marginBottom: 16 },
  practiceLabel: { fontSize: 11, letterSpacing: 1.5, textTransform: "uppercase", color: C.muted, marginBottom: 4 },
  practiceText: { fontSize: 14, lineHeight: 22, color: C.text },
  saveButton: { borderWidth: 1, borderColor: C.accent, borderRadius: 999, paddingVertical: 10, alignItems: "center", marginBottom: 8 },
  saveButtonText: { color: C.accent, fontWeight: "600", fontSize: 14 },
  tapHint: { fontSize: 11, color: C.muted, textAlign: "center", letterSpacing: 0.5 },
});
'''

# 2. CollectionScreen (app/collection.tsx)
COLLECTION_TSX = '''import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from "react-native";
import { colors, spacing } from "@/theme";
import { router } from "expo-router";
import type { PoemCard } from "../types";

const MOCK_POEMS: Partial<PoemCard>[] = [
  { id: "su_same", title: "같은 물결", relation_kr: "同", tier: "free" },
  { id: "su_generates_me", title: "서리에서 온 물", relation_kr: "生我", tier: "premium" },
  { id: "su_i_generate", title: "봄을 부르는 물", relation_kr: "我生", tier: "premium" },
  { id: "su_i_control", title: "물의 손", relation_kr: "我剋", tier: "premium" },
  { id: "su_controls_me", title: "둑 안의 물", relation_kr: "剋我", tier: "premium" },
];

export default function CollectionScreen() {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Text style={styles.backText}>← 돌아가기</Text>
        </TouchableOpacity>
        <Text style={styles.title}>시조 컬렉션</Text>
        <Text style={styles.subtitle}>수(水) 기운의 5편</Text>
      </View>
      <ScrollView contentContainerStyle={styles.grid}>
        {MOCK_POEMS.map((poem, i) => (
          <View key={i} style={styles.card}>
            <Text style={styles.cardElement}>水</Text>
            <Text style={styles.cardTitle}>{poem.title}</Text>
            <Text style={styles.cardRelation}>{poem.relation_kr}</Text>
            {poem.tier === "premium" && (
               <View style={styles.lockBadge}><Text style={styles.lockText}>🔒 프리미엄</Text></View>
            )}
          </View>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  header: { padding: spacing.lg, paddingTop: spacing.xl, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  backBtn: { marginBottom: spacing.md },
  backText: { color: colors.primary, fontSize: 16, fontWeight: "600" },
  title: { fontSize: 28, fontWeight: "800", color: colors.text, marginBottom: 4 },
  subtitle: { fontSize: 16, color: colors.textMuted },
  grid: { padding: spacing.md, flexDirection: "row", flexWrap: "wrap", gap: spacing.md, justifyContent: "center" },
  card: { width: "45%", aspectRatio: 0.8, backgroundColor: colors.surface, borderRadius: 16, padding: spacing.md, borderWidth: 1, borderColor: colors.border, alignItems: "center", justifyContent: "center" },
  cardElement: { fontSize: 32, color: colors.primary, marginBottom: 8 },
  cardTitle: { fontSize: 16, fontWeight: "700", color: colors.text, textAlign: "center", marginBottom: 4 },
  cardRelation: { fontSize: 12, color: colors.textMuted },
  lockBadge: { position: "absolute", top: 8, right: 8, backgroundColor: colors.bgMuted, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 8 },
  lockText: { fontSize: 10, color: colors.textMuted, fontWeight: "700" },
});
'''

def patch_files():
    # A. PoemFlipCard.tsx 수정
    p_flip = ROOT / "frontend" / "src" / "components" / "poem" / "PoemFlipCard.tsx"
    shutil.copy2(p_flip, p_flip.with_name(p_flip.name + SUFFIX))
    p_flip.write_text(FLIP_CARD_TSX, encoding="utf-8")
    print(f"[OK] {p_flip.name} (이미지 레이어 추가)")

    # B. collection.tsx 생성
    p_col = ROOT / "frontend" / "app" / "collection.tsx"
    p_col.write_text(COLLECTION_TSX, encoding="utf-8")
    print(f"[OK] app/collection.tsx (컬렉션 뷰어 생성)")

    # C. LuckyCodeSection.tsx 수정 (버튼 추가)
    p_lucky = ROOT / "frontend" / "src" / "components" / "sections" / "LuckyCodeSection.tsx"
    text = p_lucky.read_text(encoding="utf-8")
    shutil.copy2(p_lucky, p_lucky.with_name(p_lucky.name + SUFFIX))

    # import router 추가
    if 'import { router } from "expo-router";' not in text:
        text = text.replace('import { useT } from "@/i18n";', 'import { useT } from "@/i18n";\nimport { router } from "expo-router";\nimport { TouchableOpacity } from "react-native";')

    # PoemFlipCard 아래에 버튼 추가
    old_poem = '{section.poem && <PoemFlipCard poem={section.poem} />}'
    new_poem = '''{section.poem && <PoemFlipCard poem={section.poem} />}

      <TouchableOpacity
        onPress={() => router.push("/collection")}
        style={{ marginTop: 16, padding: 12, backgroundColor: colors.surface, borderRadius: 12, borderWidth: 1, borderColor: colors.primary, alignItems: "center" }}
      >
        <Text style={{ color: colors.primary, fontWeight: "700" }}>내 시조 모아보기 (25편)</Text>
      </TouchableOpacity>'''
    
    if old_poem in text:
        text = text.replace(old_poem, new_poem)
        p_lucky.write_text(text, encoding="utf-8")
        print(f"[OK] {p_lucky.name} (컬렉션 버튼 추가)")
    else:
        print(f"[ERR] {p_lucky.name} 수정 실패 (앵커 없음)")

if __name__ == "__main__":
    patch_files()