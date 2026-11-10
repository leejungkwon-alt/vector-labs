import { useEffect, useRef, useState } from "react";
import { Animated, Easing, Platform, StyleSheet, Text, View } from "react-native";
import { Redirect } from "expo-router";
import { colors } from "@/theme";
import { useProfileStore } from "@/store/profileStore";
import { useLanguageStore } from "@/store/languageStore";

// 스플래시 설정 ---------------------------------------------------------
const MIN_SPLASH_MS = 2200;   // 글자가 다 나타나고 읽힐 만큼의 최소 표시 시간
const MAX_SPLASH_MS = 4500;   // 저장소가 준비되지 않아도 이 시간이 지나면 진행
const SKIP_INPUT_IF_PROFILE = true; // 저장된 프로필이 있으면 입력 화면 건너뛰고 홈으로 (false = 항상 입력 화면)

// 붓글씨체: +html.tsx 에서 Google Fonts(Nanum Brush Script)를 '결' 한 글자만 불러온다.
// 로드 실패 시 윈도우의 궁서체 → 명조/세리프 순으로 대체된다.
const BRUSH_FONT = Platform.select({
  web: '"Nanum Brush Script", "궁서", Gungsuh, GungsuhChe, "바탕", serif',
  default: undefined,
});

export default function Index() {
  const profileReady = useProfileStore((s) => s.ready);
  const profile = useProfileStore((s) => s.profile);
  const langReady = useLanguageStore((s) => s.ready);

  const [minElapsed, setMinElapsed] = useState(false);
  const [timedOut, setTimedOut] = useState(false);

  const markA = useRef(new Animated.Value(0)).current;
  const pronA = useRef(new Animated.Value(0)).current;
  const meanA = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const t1 = setTimeout(() => setMinElapsed(true), MIN_SPLASH_MS);
    const t2 = setTimeout(() => setTimedOut(true), MAX_SPLASH_MS);
    const native = Platform.OS !== "web";

    // 글자 → 발음기호 → 뜻 순서로 차례대로 나타난다.
    const anim = Animated.sequence([
      Animated.timing(markA, { toValue: 1, duration: 700, easing: Easing.out(Easing.cubic), useNativeDriver: native }),
      Animated.timing(pronA, { toValue: 1, duration: 450, easing: Easing.out(Easing.quad), useNativeDriver: native }),
      Animated.timing(meanA, { toValue: 1, duration: 450, easing: Easing.out(Easing.quad), useNativeDriver: native }),
    ]);
    anim.start();

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      anim.stop();
    };
  }, [markA, pronA, meanA]);

  const ready = (profileReady && langReady && minElapsed) || timedOut;

  if (ready) {
    const href = profile && SKIP_INPUT_IF_PROFILE ? "/(tabs)/home" : "/birth-input";
    return <Redirect href={href} />;
  }

  const markScale = markA.interpolate({ inputRange: [0, 1], outputRange: [0.92, 1] });
  const markShift = markA.interpolate({ inputRange: [0, 1], outputRange: [8, 0] });

  return (
    <View style={styles.container}>
      <Animated.Text
        style={[
          styles.mark,
          BRUSH_FONT ? { fontFamily: BRUSH_FONT } : null,
          { opacity: markA, transform: [{ translateY: markShift }, { scale: markScale }] },
        ]}
      >
        결
      </Animated.Text>

      <Animated.View style={{ opacity: pronA, alignItems: "center" }}>
        <Text style={styles.pron}>gyeol  [kjʌl]</Text>
      </Animated.View>

      <Animated.View style={[styles.meaningBox, { opacity: meanA }]}>
        <Text style={styles.meaningKo}>명사 · 나무·살갗·비단의 무늬, 물·바람의 흐름, 마음씨</Text>
        <Text style={styles.meaningEn}>noun · grain, texture, and flow — the natural pattern of things</Text>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.bg,
    paddingHorizontal: 32,
  },
  mark: {
    fontSize: 132,
    lineHeight: 160,
    fontWeight: "900",
    color: colors.text,
    textAlign: "center",
  },
  pron: {
    marginTop: 4,
    fontSize: 18,
    letterSpacing: 1.5,
    color: colors.primary,
    fontWeight: "600",
  },
  meaningBox: {
    marginTop: 18,
    alignItems: "center",
    gap: 6,
  },
  meaningKo: {
    fontSize: 14,
    color: colors.text,
    textAlign: "center",
    lineHeight: 20,
  },
  meaningEn: {
    fontSize: 13,
    color: colors.textMuted,
    textAlign: "center",
    lineHeight: 19,
  },
});
