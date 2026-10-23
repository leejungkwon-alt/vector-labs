// frontend/app/index.tsx
import { useEffect, useRef, useState } from "react";
import { View, Text, StyleSheet, Animated, Easing } from "react-native";
import { router } from "expo-router";
import {
  useFonts,
  NanumBrushScript_400Regular,
} from "@expo-google-fonts/nanum-brush-script";
import { useAuthStore } from "@/store/authStore";
import { useProfileStore } from "@/store/profileStore";
import { colors } from "@/theme";

const MEANINGS = [
  "실이나 줄의 가닥 (grain, texture)",
  "서로 맺어진 인연 (connection)",
  "글의 짜임새 (composition)",
];

export default function Index() {
  const ready = useAuthStore((s) => s.ready);
  const profileReady = useProfileStore((s) => s.ready);
  const profile = useProfileStore((s) => s.profile);

  const [fontsLoaded, fontError] = useFonts({
    NanumBrushScript_400Regular,
  });
  const [fontTimedOut, setFontTimedOut] = useState(false);

  // 폰트가 3초 안에 로드 안 되면 시스템 폰트로 진행
  useEffect(() => {
    const t = setTimeout(() => setFontTimedOut(true), 3000);
    return () => clearTimeout(t);
  }, []);

  useEffect(() => {
    console.log(
      "[Boot] fontsLoaded=", fontsLoaded,
      "fontError=", !!fontError,
      "ready=", ready,
      "profileReady=", profileReady,
      "profile=", !!profile,
    );
  }, [fontsLoaded, fontError, ready, profileReady, profile]);

  const canRender = fontsLoaded || !!fontError || fontTimedOut;
  const useBrushFont = !!fontsLoaded;

  // 애니메이션
  const brushOpacity = useRef(new Animated.Value(0)).current;
  const brushScale   = useRef(new Animated.Value(0.85)).current;
  const brushY       = useRef(new Animated.Value(12)).current;
  const pronOpacity  = useRef(new Animated.Value(0)).current;
  const meaningsOp   = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.sequence([
      Animated.parallel([
        Animated.timing(brushOpacity, {
          toValue: 1, duration: 900,
          easing: Easing.out(Easing.cubic), useNativeDriver: true,
        }),
        Animated.timing(brushScale, {
          toValue: 1, duration: 900,
          easing: Easing.out(Easing.back(1.1)), useNativeDriver: true,
        }),
        Animated.timing(brushY, {
          toValue: 0, duration: 900,
          easing: Easing.out(Easing.cubic), useNativeDriver: true,
        }),
      ]),
      Animated.timing(pronOpacity, {
        toValue: 1, duration: 350, useNativeDriver: true,
      }),
      Animated.timing(meaningsOp, {
        toValue: 1, duration: 450, useNativeDriver: true,
      }),
    ]).start();
  }, []);

  useEffect(() => {
    if (!canRender || !ready || !profileReady) return;
    const t = setTimeout(() => {
      router.replace(profile ? "/(tabs)/home" : "/birth-input");
    }, 2600);
    return () => clearTimeout(t);
  }, [canRender, ready, profileReady, profile]);

  if (!canRender) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingHint}>loading…</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.heroWrap}>
        <Animated.Text
          style={[
            styles.brushText,
            {
              fontFamily: useBrushFont
                ? "NanumBrushScript_400Regular"
                : undefined,
              opacity: brushOpacity,
              transform: [{ scale: brushScale }, { translateY: brushY }],
            },
          ]}
        >
          결
        </Animated.Text>

        <Animated.Text
          style={[styles.pronunciation, { opacity: pronOpacity }]}
        >
          [gyeol]
        </Animated.Text>
      </View>

      <Animated.View style={{ opacity: meaningsOp, alignItems: "center" }}>
        <Text style={styles.meaningLabel}>사전적 의미</Text>
        {MEANINGS.map((m, i) => (
          <Text key={i} style={styles.meaningText}>
            {i + 1}. {m}
          </Text>
        ))}
      </Animated.View>

      <Animated.Text style={[styles.tagline, { opacity: meaningsOp }]}>
        Reading the grain of your life
      </Animated.Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bg,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 32,
  },
  loadingHint: {
    fontSize: 12,
    color: colors.textMuted,
    letterSpacing: 4,
  },
  heroWrap: {
    alignItems: "center",
    marginBottom: 40,
  },
  brushText: {
    fontSize: 140,
    lineHeight: 160,
    color: colors.primary,
    textAlign: "center",
    includeFontPadding: false,
    fontWeight: "300", // 시스템 폰트 폴백 시에도 얇게
  },
  pronunciation: {
    fontSize: 16,
    color: colors.textMuted,
    letterSpacing: 3,
    marginTop: 4,
    fontStyle: "italic",
  },
  meaningLabel: {
    fontSize: 11,
    color: colors.textMuted,
    letterSpacing: 2,
    marginBottom: 10,
  },
  meaningText: {
    fontSize: 13,
    color: colors.text,
    textAlign: "center",
    lineHeight: 22,
    opacity: 0.85,
  },
  tagline: {
    position: "absolute",
    bottom: 60,
    fontSize: 11,
    color: colors.textMuted,
    letterSpacing: 1.5,
  },
});
