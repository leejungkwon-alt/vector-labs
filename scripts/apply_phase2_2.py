import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUFFIX = f".bak_phase2_2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# 1. 예쁜 SVG 이미지 25쌍(서예/배경화면) 생성
def generate_svgs():
    asset_dir = ROOT / "frontend" / "assets" / "poems"
    asset_dir.mkdir(parents=True, exist_ok=True)
    
    # 5오행 색상 테마
    colors = {
        "mok": ("#2E5C4E", "#E8F0E8"),  # 木 (Wood)
        "hwa": ("#B83A30", "#FDE8E6"),  # 火 (Fire)
        "to":  ("#A67C52", "#F5ECE1"),  # 土 (Earth)
        "geum":("#6B7280", "#F3F4F6"),  # 金 (Metal)
        "su":  ("#1E3A8A", "#E6EEF8"),  # 水 (Water)
    }
    relations = ["same", "generates_me", "i_generate", "i_control", "controls_me"]
    labels = {"mok": "木", "hwa": "火", "to": "土", "geum": "金", "su": "水"}
    
    for elem, (dark, light) in colors.items():
        for rel in relations:
            pid = f"{elem}_{rel}"
            
            # 서예 이미지 (앞면용)
            callig = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400" viewBox="0 0 800 400">
  <rect width="800" height="400" fill="{light}"/>
  <text x="50%" y="55%" dominant-baseline="middle" text-anchor="middle" 
        font-family="serif" font-size="200" fill="{dark}" opacity="0.8">{labels[elem]}</text>
</svg>'''
            (asset_dir / f"{pid}_calligraphy.svg").write_text(callig, encoding="utf-8")
            
            # 배경화면 이미지 (뒷면 다운로드용)
            wall = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">
  <rect width="1080" height="1920" fill="{dark}"/>
  <circle cx="540" cy="960" r="400" fill="{light}" opacity="0.1"/>
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" 
        font-family="serif" font-size="400" fill="{light}" opacity="0.3">{labels[elem]}</text>
</svg>'''
            (asset_dir / f"{pid}_wallpaper.svg").write_text(wall, encoding="utf-8")
            
    print(f"[OK] 25쌍의 SVG 이미지 생성 완료 ({asset_dir})")

# 2. PoemFlipCard.tsx 수정 (실제 SVG 이미지 로드 및 다운로드 구현)
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
  poem, lang, onSubscribePress,
}: {
  poem: PoemCard;
  lang?: string;
  onSubscribePress?: () => void;
}) {
  const [flipped, setFlipped] = useState(false);
  const anim = useRef(new Animated.Value(0)).current;

  const flip = () => {
    Animated.timing(anim, {
      toValue: flipped ? 0 : 1, duration: 420, useNativeDriver: USE_NATIVE,
    }).start();
    setFlipped(!flipped);
  };

  const frontRotate = anim.interpolate({ inputRange: [0, 1], outputRange: ["0deg", "180deg"] });
  const backRotate  = anim.interpolate({ inputRange: [0, 1], outputRange: ["180deg", "360deg"] });
  const frontOpacity = anim.interpolate({ inputRange: [0, 0.5, 0.5, 1], outputRange: [1, 1, 0, 0] });
  const backOpacity  = anim.interpolate({ inputRange: [0, 0.5, 0.5, 1], outputRange: [0, 0, 1, 1] });

  const isWallpaperLocked = (poem.locked_fields || []).includes("wallpaper_image");

  const handleSaveWallpaper = () => {
    if (isWallpaperLocked) { onSubscribePress?.(); return; }
    
    const url = `/assets/poems/${poem.id}_wallpaper.svg`;
    if (Platform.OS === "web") {
      const a = document.createElement("a");
      a.href = url;
      a.download = `${poem.id}_wallpaper.svg`;
      a.click();
    } else {
      Alert.alert("알림", "모바일 앱에서는 곧 지원될 예정입니다.");
    }
  };

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
            <Image source={{ uri: `/assets/poems/${poem.id}_calligraphy.svg` }} style={styles.image} resizeMode="cover" />
            <Text style={styles.elementBadge}>{poem.element}</Text>
            <Text style={styles.sijoText}>{poem.sijo_ko}</Text>
            {poem.keywords && poem.keywords.length > 0 && (
              <View style={styles.keywordRow}>
                {poem.keywords.map((k, i) => <Text key={i} style={styles.keyword}>#{k}</Text>)}
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
            <Pressable onPress={handleSaveWallpaper} style={styles.saveButton}>
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
  image: { width: "100%", height: 130, borderRadius: 12, marginBottom: 16, backgroundColor: C.accentSoft },
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

# 3. Collection.tsx 수정 (실제 데이터 및 프리미엄 UI 적용)
COLLECTION_TSX = '''import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Image } from "react-native";
import { colors, spacing, radius } from "@/theme";
import { router } from "expo-router";
import { useAuthStore } from "@/store/authStore";

const POEMS = [
  { id: "su_same", title: "같은 물결", relation: "同", tier: "free" },
  { id: "su_generates_me", title: "서리에서 온 물", relation: "生我", tier: "premium" },
  { id: "su_i_generate", title: "봄을 부르는 물", relation: "我生", tier: "premium" },
  { id: "su_i_control", title: "물의 손", relation: "我剋", tier: "premium" },
  { id: "su_controls_me", title: "둑 안의 물", relation: "剋我", tier: "premium" },
];

export default function CollectionScreen() {
  const user = useAuthStore((s) => s.user);
  const isPremium = user?.tier === "premium" || user?.tier === "subscription";

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
        {POEMS.map((poem, i) => {
          const locked = poem.tier === "premium" && !isPremium;
          return (
            <View key={i} style={[styles.card, locked && { opacity: 0.7 }]}>
              <Image source={{ uri: `/assets/poems/${poem.id}_calligraphy.svg` }} style={styles.cardImg} />
              <Text style={styles.cardTitle}>{poem.title}</Text>
              <Text style={styles.cardRelation}>{poem.relation}</Text>
              {locked && (
                 <View style={styles.lockOverlay}>
                   <Text style={styles.lockText}>🔒 프리미엄</Text>
                 </View>
              )}
            </View>
          );
        })}
      </ScrollView>
      {!isPremium && (
        <View style={styles.footer}>
          <Text style={styles.footerText}>프리미엄으로 업그레이드하고 25편 전체를 감상하세요.</Text>
        </View>
      )}
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
  card: { width: "45%", backgroundColor: colors.surface, borderRadius: 16, padding: spacing.md, borderWidth: 1, borderColor: colors.border, alignItems: "center", justifyContent: "center", position: "relative", overflow: "hidden" },
  cardImg: { width: "100%", height: 80, borderRadius: 8, marginBottom: 8, backgroundColor: colors.bgMuted },
  cardTitle: { fontSize: 16, fontWeight: "700", color: colors.text, textAlign: "center", marginBottom: 4 },
  cardRelation: { fontSize: 12, color: colors.textMuted },
  lockOverlay: { ...StyleSheet.absoluteFillObject, backgroundColor: "rgba(0,0,0,0.4)", alignItems: "center", justifyContent: "center" },
  lockText: { color: "#fff", fontWeight: "700", fontSize: 14 },
  footer: { padding: spacing.lg, backgroundColor: colors.primarySoft, alignItems: "center" },
  footerText: { color: colors.primary, fontWeight: "600" }
});
'''

def main():
    # 1. SVG 이미지 생성
    generate_svgs()

    # 2. PoemFlipCard 덮어쓰기
    p_flip = ROOT / "frontend" / "src" / "components" / "poem" / "PoemFlipCard.tsx"
    shutil.copy2(p_flip, p_flip.with_name(p_flip.name + SUFFIX))
    p_flip.write_text(FLIP_CARD_TSX, encoding="utf-8")
    print("[OK] PoemFlipCard.tsx (실제 SVG 이미지 및 다운로드 적용)")

    # 3. Collection 덮어쓰기
    p_col = ROOT / "frontend" / "app" / "collection.tsx"
    shutil.copy2(p_col, p_col.with_name(p_col.name + SUFFIX))
    p_col.write_text(COLLECTION_TSX, encoding="utf-8")
    print("[OK] collection.tsx (실제 데이터 및 프리미엄 게이팅 적용)")

if __name__ == "__main__":
    main()