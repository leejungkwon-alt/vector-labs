#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2: 프론트 시조 플립 카드 적용.

생성:
  frontend/src/components/poem/PoemFlipCard.tsx

패치:
  frontend/src/components/sections/LuckyCodeSection.tsx (import + render)
  frontend/types.ts (PoemCard 타입 + poem 필드)

실행:
  $env:PYTHONPATH=(Get-Location).Path
  python scripts\\apply_phase2_flip_card.py
"""
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUFFIX = f".bak_phase2fc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

FLIP_CARD_TSX = '''import { useRef, useState } from "react";
import { View, Text, Pressable, Animated, StyleSheet, Alert, Platform } from "react-native";
import { colors } from "@/theme";
import type { PoemCard } from "../../../types";

const FACE_HEIGHT = 420;
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

  return (
    <View style={{ marginVertical: 16 }}>
      <Text style={styles.caption}>
        {tt(lang, "오늘의 시조", "Poem of the Day")} · {poem.relation_kr}
      </Text>

      <Pressable onPress={flip} accessibilityRole="button"
                 accessibilityLabel={tt(lang, "시조 카드 뒤집기", "Flip poem card")}>
        <View style={{ height: FACE_HEIGHT, position: "relative" }}>
          <Animated.View
            pointerEvents={flipped ? "none" : "auto"}
            style={[StyleSheet.absoluteFillObject, styles.face,
                    { opacity: frontOpacity,
                      transform: [{ perspective: 900 }, { rotateY: frontRotate }] }]}
          >
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
                    { opacity: backOpacity,
                      transform: [{ perspective: 900 }, { rotateY: backRotate }] }]}
          >
            <Text style={styles.title}>{poem.title}</Text>
            <Text style={styles.romanization}>{poem.romanization}</Text>
            <View style={styles.divider} />
            <Text style={styles.interpretation}>{poem.interpretation}</Text>
            {poem.practice ? (
              <View style={styles.practiceBox}>
                <Text style={styles.practiceLabel}>
                  {tt(lang, "오늘의 실천", "Today's Practice")}
                </Text>
                <Text style={styles.practiceText}>{poem.practice}</Text>
              </View>
            ) : null}
            <Pressable onPress={onSaveWallpaper} style={styles.saveButton}>
              <Text style={styles.saveButtonText}>
                {isWallpaperLocked
                  ? tt(lang, "배경화면 · 프리미엄", "Wallpaper · Premium")
                  : tt(lang, "배경화면 저장", "Save wallpaper")}
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
  caption: {
    fontSize: 11, letterSpacing: 2, textTransform: "uppercase",
    color: C.muted, textAlign: "center", marginBottom: 8,
  },
  face: {
    backgroundColor: C.bg, borderRadius: 20, padding: 24,
    borderWidth: 1, borderColor: C.border,
    justifyContent: "center",
    shadowColor: "#000", shadowOpacity: 0.08, shadowRadius: 12,
    shadowOffset: { width: 0, height: 4 },
  },
  elementBadge: {
    fontSize: 44, textAlign: "center", marginBottom: 20,
    color: C.accent, fontWeight: "200",
  },
  sijoText: {
    fontSize: 20, lineHeight: 34, textAlign: "center",
    color: C.text, marginBottom: 20, fontWeight: "300",
  },
  keywordRow: {
    flexDirection: "row", flexWrap: "wrap",
    justifyContent: "center", gap: 6, marginBottom: 16,
  },
  keyword: {
    fontSize: 12, color: C.muted,
    paddingHorizontal: 8, paddingVertical: 4,
    borderWidth: 1, borderColor: C.border, borderRadius: 999,
  },
  title: { fontSize: 22, fontWeight: "600", textAlign: "center", color: C.text, marginBottom: 8 },
  romanization: { fontSize: 12, fontStyle: "italic", textAlign: "center", color: C.muted, marginBottom: 12 },
  divider: { height: 1, backgroundColor: C.border, marginVertical: 12 },
  interpretation: { fontSize: 15, lineHeight: 24, color: C.text, marginBottom: 16 },
  practiceBox: { backgroundColor: C.accentSoft, padding: 12, borderRadius: 12, marginBottom: 16 },
  practiceLabel: { fontSize: 11, letterSpacing: 1.5, textTransform: "uppercase", color: C.muted, marginBottom: 4 },
  practiceText: { fontSize: 14, lineHeight: 22, color: C.text },
  saveButton: {
    borderWidth: 1, borderColor: C.accent, borderRadius: 999,
    paddingVertical: 10, alignItems: "center", marginBottom: 8,
  },
  saveButtonText: { color: C.accent, fontWeight: "600", fontSize: 14 },
  tapHint: { fontSize: 11, color: C.muted, textAlign: "center", letterSpacing: 0.5 },
});
'''

TYPES_ADD = '''
// ---- Phase 2: 시조 카드 ----
export type PoemRelation =
  | "same"
  | "generates_me"
  | "i_generate"
  | "i_control"
  | "controls_me";

export interface PoemCard {
  id: string;
  element: string;
  element_idx: number;
  relation: PoemRelation;
  relation_kr: string;
  title: string;
  sijo_ko: string;
  romanization: string;
  interpretation: string;
  practice: string;
  calligraphy_image: string;
  wallpaper_image: string | null;
  keywords: string[];
  tier: "free" | "premium";
  locked_fields?: string[];
  collection?: PoemCard[];
}
'''


def _bak(p: Path):
    bak = p.with_name(p.name + SUFFIX)
    shutil.copy2(p, bak)
    print(f"  [backup] {bak.name}")


def create_flip_card():
    path = ROOT / "frontend" / "src" / "components" / "poem" / "PoemFlipCard.tsx"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        print(f"[SKIP] {path.relative_to(ROOT)} already exists")
        return
    path.write_text(FLIP_CARD_TSX, encoding="utf-8")
    print(f"[OK]   {path.relative_to(ROOT)}")


def patch_types():
    path = ROOT / "frontend" / "types.ts"
    text = path.read_text(encoding="utf-8")
    if "export interface PoemCard" in text:
        print(f"[SKIP] {path.relative_to(ROOT)} already patched")
        return
    _bak(path)

    anchor = 'export interface LuckyCodeSection extends ReportSectionBase {'
    if text.count(anchor) != 1:
        print(f"[ERR] LuckyCodeSection anchor not unique: {text.count(anchor)}")
        sys.exit(1)
    text = text.replace(anchor, TYPES_ADD.strip() + "\n\n" + anchor, 1)

    old_power = '  power: LuckyCodePower;\n'
    if text.count(old_power) != 1:
        print(f"[ERR] power anchor not unique: {text.count(old_power)}")
        sys.exit(1)
    text = text.replace(old_power, old_power + '  poem?: PoemCard;\n', 1)

    path.write_text(text, encoding="utf-8")
    print(f"[OK]   {path.relative_to(ROOT)} (+PoemCard)")


def patch_lucky_code():
    path = ROOT / "frontend" / "src" / "components" / "sections" / "LuckyCodeSection.tsx"
    text = path.read_text(encoding="utf-8")
    if "PoemFlipCard" in text:
        print(f"[SKIP] {path.relative_to(ROOT)} already patched")
        return
    _bak(path)

    old_import = 'import type { LuckyCodeSection } from "../../../types";'
    new_import = (
        'import type { LuckyCodeSection } from "../../../types";\n'
        'import { PoemFlipCard } from "../poem/PoemFlipCard";'
    )
    if text.count(old_import) != 1:
        print(f"[ERR] import anchor not unique: {text.count(old_import)}")
        sys.exit(1)
    text = text.replace(old_import, new_import, 1)

    old_hero = '      <Text style={ss.coreHero}>{section.hero}</Text>'
    new_hero = (
        '      <Text style={ss.coreHero}>{section.hero}</Text>\n\n'
        '      {section.poem && <PoemFlipCard poem={section.poem} />}'
    )
    if text.count(old_hero) != 1:
        print(f"[ERR] hero anchor not unique: {text.count(old_hero)}")
        sys.exit(1)
    text = text.replace(old_hero, new_hero, 1)

    path.write_text(text, encoding="utf-8")
    print(f"[OK]   {path.relative_to(ROOT)} (+PoemFlipCard render)")


def main():
    print("=" * 60)
    print("Phase 2: 프론트 플립 카드 적용")
    print("=" * 60)
    print(f"ROOT = {ROOT}\n")

    create_flip_card()
    patch_types()
    patch_lucky_code()

    print("\n" + "=" * 60)
    print("[SUCCESS] 프론트 패치 완료")
    print("=" * 60)
    print("""
다음 단계:
  1. 로컬 웹 미리보기:
       cd frontend
       npx expo start --web

  2. 프론트 빌드 + Vercel 배포:
       npx expo export --platform web
       cd dist
       npx vercel deploy --prod
""")


if __name__ == "__main__":
    main()