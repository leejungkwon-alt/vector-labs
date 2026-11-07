import { useRef, useState } from "react";
import { View, Text, Pressable, Animated, StyleSheet, Alert, Platform, Image } from "react-native";
import { colors } from "@/theme";
import { useLanguageStore } from "@/store/languageStore";
import type { PoemCard } from "../../../types";
import { getRelationLabel } from "@/utils/poemRelations";

const FACE_HEIGHT = 560;
const USE_NATIVE = Platform.OS !== "web";

const C = {
  bg: (colors as any).bg || (colors as any).card || "#FBF8F2",
  border: (colors as any).border || "#E5DDD0",
  text: (colors as any).text || "#2A2620",
  muted: (colors as any).muted || "#8A8378",
  accent: (colors as any).accent || (colors as any).primary || "#B8860B",
  accentSoft: (colors as any).accentSoft || (colors as any).primarySoft || "#F5EBD8",
};

const LANG_MAP: Record<string, Record<string, string>> = {
  es: {
    "오늘의 시조": "Poema del Día",
    "탭하여 뒤집기 →": "Toca para voltear →",
    "← 탭하여 돌아가기": "← Toca para volver",
    "오늘의 실천": "Práctica de Hoy",
    "배경화면 · 프리미엄": "Fondo de pantalla · Premium",
    "배경화면 저장": "Guardar fondo"
  },
  ja: {
    "오늘의 시조": "今日の詩",
    "탭하여 뒤집기 →": "タップして裏返す →",
    "← 탭하여 돌아가기": "← タップして戻る",
    "오늘의 실천": "今日の実践",
    "배경화면 · 프리미엄": "壁紙 · プレミアム",
    "배경화면 저장": "壁紙を保存"
  },
  zh_cn: {
    "오늘의 시조": "今日诗歌",
    "탭하여 뒤집기 →": "点击翻转 →",
    "← 탭하여 돌아가기": "← 点击返回",
    "오늘의 실천": "今日实践",
    "배경화면 · 프리미엄": "壁纸 · 高级",
    "배경화면 저장": "保存壁纸"
  }
};

function tt(lang: string | undefined, ko: string, en: string): string {
  const l = lang || "en";
  if (l === "ko") return ko;
  if (l === "en") return en;
  return LANG_MAP[l]?.[ko] || en;
}

export function PoemFlipCard({
  poem, lang, onSubscribePress,
}: {
  poem: PoemCard;
  lang?: string;
  onSubscribePress?: () => void;
}) {
  const storeLang = useLanguageStore((s) => s.lang);
  const currentLang = lang || storeLang || "en";
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

  const handleSaveWallpaper = async () => {
    if (isWallpaperLocked) { onSubscribePress?.(); return; }
    
    const wallpaperSrc = `/assets/poems/${poem.id}_wallpaper.png`;
    
    if (Platform.OS !== "web") {
      Alert.alert("알림", "모바일 앱에서는 곧 지원될 예정입니다.");
      return;
    }
    
    try {
      // 1. 배경 이미지 로드
      const img = new window.Image();
      img.crossOrigin = "anonymous";
      await new Promise<void>((resolve, reject) => {
        img.onload = () => resolve();
        img.onerror = () => reject(new Error("배경 이미지 로드 실패"));
        img.src = wallpaperSrc;
      });
      
      // 2. 캔버스 생성
      const canvas = document.createElement("canvas");
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext("2d");
      if (!ctx) throw new Error("Canvas 2D 컨텍스트 없음");
      
      const W = img.width;
      const H = img.height;
      
      // 3. 배경 그리기
      ctx.drawImage(img, 0, 0);
      
      // 4. 하단 그라데이션 오버레이 (텍스트 가독성)
      const overlayH = H * 0.5;
      const grad = ctx.createLinearGradient(0, H - overlayH, 0, H);
      grad.addColorStop(0, "rgba(0,0,0,0)");
      grad.addColorStop(0.4, "rgba(0,0,0,0.55)");
      grad.addColorStop(1, "rgba(0,0,0,0.82)");
      ctx.fillStyle = grad;
      ctx.fillRect(0, H - overlayH, W, overlayH);
      
      // 5. 폰트 크기
      const titleSize = Math.round(W * 0.07);
      const sijoSize = Math.round(W * 0.05);
      const romanSize = Math.round(W * 0.025);
      
      ctx.textAlign = "center";
      ctx.shadowColor = "rgba(0,0,0,0.8)";
      ctx.shadowBlur = 12;
      
      // 6. 제목
      ctx.font = `bold ${titleSize}px "Noto Serif KR", "Noto Serif", serif`;
      ctx.fillStyle = "rgba(255,255,255,0.98)";
      const titleY = H - overlayH + titleSize * 1.5;
      ctx.fillText(poem.title || "", W / 2, titleY);
      
      // 7. 시조 본문
      ctx.font = `${sijoSize}px "Noto Serif KR", "Noto Serif", serif`;
      ctx.fillStyle = "rgba(240,245,255,0.95)";
      const sijoText = poem.sijo || poem.sijo_ko || "";
      const sijoLines = sijoText.split(/\n|\\n/).map((s: string) => s.trim()).filter(Boolean);
      const sijoStartY = titleY + sijoSize * 2.2;
      sijoLines.forEach((line: string, i: number) => {
        ctx.fillText(line, W / 2, sijoStartY + i * sijoSize * 1.6);
      });
      
      // 8. 로마자 (한국어일 때만)
      if (poem.romanization && currentLang === "ko") {
        ctx.font = `italic ${romanSize}px "Noto Serif KR", "Noto Serif", serif`;
        ctx.fillStyle = "rgba(200,220,255,0.65)";
        ctx.shadowBlur = 4;
        const romanY = sijoStartY + sijoLines.length * sijoSize * 1.6 + romanSize * 1.8;
        ctx.fillText(poem.romanization, W / 2, romanY);
      }
      
      // 9. URL 워터마크
      const wmSize = Math.round(W * 0.024);
      ctx.font = `italic ${wmSize}px "Noto Sans KR", sans-serif`;
      ctx.fillStyle = "rgba(255,255,255,0.5)";
      ctx.shadowBlur = 0;
      ctx.fillText("gyeol.app", W / 2, H - W * 0.03);
      
      // 10. 다운로드
      await new Promise<void>((resolve) => {
        canvas.toBlob((blob) => {
          if (!blob) return resolve();
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = `${poem.id}_wallpaper.png`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
          resolve();
        }, "image/png", 0.95);
      });
    } catch (e: any) {
      console.error("[wallpaper save]", e);
      alert(`배경화면 생성 중 오류: ${e?.message || "알 수 없는 오류"}`);
    }
  };

  return (
    <View style={{ marginVertical: 16 }}>
      <Text style={styles.caption}>
        {tt(currentLang, "오늘의 시조", "Poem of the Day")} · {getRelationLabel(poem.relation, currentLang)}
      </Text>

      <Pressable onPress={flip} accessibilityRole="button">
        <View style={{ height: FACE_HEIGHT, position: "relative" }}>
          <Animated.View
            pointerEvents={flipped ? "none" : "auto"}
            style={[StyleSheet.absoluteFill, styles.face,
                    { opacity: frontOpacity, transform: [{ perspective: 900 }, { rotateY: frontRotate }] }]}
          >
            <Image source={{ uri: `/assets/poems/${poem.id}_calligraphy.png` }} style={styles.image} resizeMode="cover" />
            <Text style={styles.elementBadge}>{poem.element}</Text>
            <Text style={styles.sijoText}>{poem.sijo || poem.sijo_ko}</Text>
            {poem.keywords && poem.keywords.length > 0 && (
              <View style={styles.keywordRow}>
                {poem.keywords.map((k, i) => <Text key={i} style={styles.keyword}>#{k}</Text>)}
              </View>
            )}
            <Text style={styles.tapHint}>{tt(currentLang, "탭하여 뒤집기 →", "Tap to flip →")}</Text>
          </Animated.View>

          <Animated.View
            pointerEvents={flipped ? "auto" : "none"}
            style={[StyleSheet.absoluteFill, styles.face,
                    { opacity: backOpacity, transform: [{ perspective: 900 }, { rotateY: backRotate }] }]}
          >
            <Text style={styles.title}>{poem.title}</Text>
                        <Text style={styles.romanization}>{poem.romanization}</Text>
            <View style={styles.divider} />
            {poem.commentary ? <Text style={styles.commentary}>{poem.commentary}</Text> : null}
            <View style={styles.divider} />
            <Text style={styles.interpretation}>{poem.interpretation}</Text>
            {poem.practice ? (
              <View style={styles.practiceBox}>
                <Text style={styles.practiceLabel}>{tt(currentLang, "오늘의 실천", "Today's Practice")}</Text>
                <Text style={styles.practiceText}>{poem.practice}</Text>
              </View>
            ) : null}
            <Pressable onPress={handleSaveWallpaper} style={styles.saveButton}>
              <Text style={styles.saveButtonText}>
                {isWallpaperLocked ? tt(currentLang, "배경화면 · 프리미엄", "Wallpaper · Premium") : tt(currentLang, "배경화면 저장", "Save wallpaper")}
              </Text>
            </Pressable>
            <Text style={styles.tapHint}>{tt(currentLang, "← 탭하여 돌아가기", "← Tap to flip back")}</Text>
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
  title: { fontSize: 22, fontWeight: "600", textAlign: "center", color: C.text, marginBottom: 4 },
  poet: { fontSize: 14, textAlign: "center", color: C.accent, marginBottom: 8, fontStyle: "italic" },
  commentary: { fontSize: 14, lineHeight: 22, color: C.text, fontStyle: "italic", marginBottom: 8 },
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
