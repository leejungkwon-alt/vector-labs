import { useEffect, useState } from "react";

// [TMA] 텔레그램 SDK 로드 (앱 실행 최우선)
if (typeof window !== "undefined") {
  const script = document.createElement("script");
  script.src = "https://telegram.org/js/telegram-web-app.js";
  script.async = false; // 동기적으로 로드하여 해시 파싱 보장
  document.head.appendChild(script);
}
import { Stack } from "expo-router";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { StatusBar } from "expo-status-bar";
import * as SplashScreen from "expo-splash-screen";
import { View, ActivityIndicator, StyleSheet } from "react-native";
import { useAuthStore } from "@/store/authStore";
import { useProfileStore } from "@/store/profileStore";
import { useLanguageStore } from "@/store/languageStore";
import { colors } from "@/theme";

// 앱이 준비될 때까지 스플래시 화면 유지
SplashScreen.preventAutoHideAsync().catch(() => {});

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 60_000, retry: 1 } },
});

export default function RootLayout() {
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