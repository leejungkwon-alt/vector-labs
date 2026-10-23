import { useLanguageStore } from "@/store/languageStore"; // SAJU-PATCH:loadLang
﻿import { useEffect } from "react";
import { Stack } from "expo-router";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { StatusBar } from "expo-status-bar";
import { useAuthStore } from "@/store/authStore";
import { useProfileStore } from "@/store/profileStore";

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 60_000, retry: 1 } },
});

export default function RootLayout() {
  const bootstrap = useAuthStore((s) => s.bootstrap);
  const loadProfile = useProfileStore((s) => s.loadProfile);

  const loadLang = useLanguageStore((s) => s.loadLang); // SAJU-PATCH:loadLang


  useEffect(() => {
    bootstrap();
    loadLang(); // // SAJU-PATCH:loadLang
    loadProfile();
  }, [bootstrap, loadProfile, loadLang]);

  return (
    <SafeAreaProvider>
      <QueryClientProvider client={queryClient}>
        <StatusBar style="dark" />
        <Stack screenOptions={{ headerShown: false }}>
          <Stack.Screen name="index" />
          <Stack.Screen name="birth-input" options={{ title: "출생 정보 입력", headerShown: true }} />
          <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        </Stack>
      </QueryClientProvider>
    </SafeAreaProvider>
  );
}
