import { useEffect, useState } from "react";
import { useTelegramUX } from "@/hooks/useTelegramUX";
import { Stack } from "expo-router";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { StatusBar } from "expo-status-bar";
import * as SplashScreen from "expo-splash-screen";
// 17번째 줄에 있던 Platform을 여기로 올렸습니다.
import { View, ActivityIndicator, StyleSheet, Platform } from "react-native"; 
import { useAuthStore } from "@/store/authStore";
import { useProfileStore } from "@/store/profileStore";
import { useLanguageStore } from "@/store/languageStore";
import { colors } from "@/theme";

// [TMA] 텔레그램 SDK 로드 (웹 브라우저에서만 실행되도록 변경)
if (Platform.OS === "web") {
  const script = document.createElement("script");
  script.src = "https://telegram.org/js/telegram-web-app.js";
  script.async = false;
  document.head.appendChild(script);
}

// 앱 준비될 때까지 스플래시 화면 유지
SplashScreen.preventAutoHideAsync().catch(() => {});

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 60_000, retry: 1 } },
});

export default function RootLayout() {
  // ... (이하 기존 코드는 그대로 두시면 됩니다)
  useTelegramUX();
  useEffect(() => {
    if (typeof document !== "undefined" && Platform.OS === "web") {
      const style = document.createElement("style");
      style.innerHTML = `
        body, div, span, p, h1, h2, h3, h4, h5, h6, input, textarea, button, a, li, label {
          font-family: "Malgun Gothic", "Apple SD Gothic Neo", "Noto Sans KR", sans-serif !important;
        }
      `;
      document.head.appendChild(style);
      return () => { document.head.removeChild(style); };
    }
  }, []);

  const bootstrap = useAuthStore((s) => s.bootstrap);
  const loadProfile = useProfileStore((s) => s.loadProfile);
  const loadLang = useLanguageStore((s) => s.loadLang);
  const [appReady, setAppReady] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined" && (window as any).Telegram?.WebApp) {
      const tg = (window as any).Telegram.WebApp;
      tg.ready();
      tg.expand();
      tg.disableVerticalSwipes?.();
    }
  }, []);

  useEffect(() => {
    async function prepare() {
      try {
        await bootstrap();
        await Promise.all([loadLang(), loadProfile()]);
      } catch (e) {
        console.warn("Initialization error:", e);
      } finally {
        setAppReady(true);
        SplashScreen.hideAsync().catch(() => {});
      }
    }
    prepare();
  }, [bootstrap, loadProfile, loadLang]);

  if (!appReady) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  return (
    <SafeAreaProvider>
      <QueryClientProvider client={queryClient}>
        <StatusBar style="dark" />
        <Stack screenOptions={{ headerShown: false }}>
          <Stack.Screen name="index" />
          <Stack.Screen name="birth-input" options={{ title: "", headerShown: true }} />
          <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        </Stack>
      </QueryClientProvider>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#ffffff",
  },
});