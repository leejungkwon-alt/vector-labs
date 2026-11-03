import { Tabs } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { colors } from "@/theme";
import { useT } from "@/i18n";

export default function TabsLayout() {
  const t = useT();
  const insets = useSafeAreaInsets();
  const tg = typeof window !== "undefined" ? (window as any).Telegram?.WebApp : null;
  const tgBottom = (tg?.safeAreaInset?.bottom ?? 0) + (tg?.contentSafeAreaInset?.bottom ?? 0);
  const bottom = Math.max(insets.bottom, tgBottom, 8);

  return (
    <Tabs screenOptions={{
      tabBarActiveTintColor: colors.primary,
      tabBarInactiveTintColor: colors.textMuted,
      tabBarLabelStyle: { fontSize: 14, fontWeight: "700" },
      tabBarIconStyle: { display: "none" },
      tabBarItemStyle: { justifyContent: "center" },
      tabBarStyle: { height: 52 + bottom, paddingTop: 6, paddingBottom: bottom },
      headerShown: true,
    }}>
      <Tabs.Screen name="home" options={{ title: t("tabs.home"), tabBarIcon: () => null }} />
      <Tabs.Screen name="daily" options={{ title: t("tabs.daily"), tabBarIcon: () => null }} />
      <Tabs.Screen name="compatibility" options={{ title: t("tabs.compatibility"), tabBarIcon: () => null }} />
      <Tabs.Screen name="settings" options={{ title: t("tabs.settings"), tabBarIcon: () => null }} />
    </Tabs>
  );
}