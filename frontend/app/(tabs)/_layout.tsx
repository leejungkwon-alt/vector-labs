import { Tabs } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "@/theme";
import { useT } from "@/i18n";

export default function TabsLayout() {
  const t = useT();

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textMuted,
        tabBarStyle: { backgroundColor: colors.surface, borderTopColor: colors.border },
        headerShown: true,
        headerStyle: { backgroundColor: colors.surface },
        headerTitleStyle: { color: colors.text },
      }}
    >
      <Tabs.Screen
        name="home"
        options={{
          title: t("tabs.home"),
          tabBarIcon: ({ color }) => (
            <Ionicons name="sunny-outline" size={24} color={(color as string | undefined) || "#7A6A5C"} />
          ),
        }}
      />
      <Tabs.Screen
        name="daily"
        options={{
          title: t("tabs.daily"),
          tabBarIcon: ({ color }) => (
            <Ionicons name="calendar-outline" size={24} color={(color as string | undefined) || "#7A6A5C"} />
          ),
        }}
      />
      <Tabs.Screen
        name="compatibility"
        options={{
          title: t("tabs.compatibility"),
          tabBarIcon: ({ color }) => (
            <Ionicons name="heart-outline" size={24} color={(color as string | undefined) || "#7A6A5C"} />
          ),
        }}
      />
      <Tabs.Screen
        name="settings"
        options={{
          title: t("tabs.settings"),
          tabBarIcon: ({ color }) => (
            <Ionicons name="settings-outline" size={24} color={(color as string | undefined) || "#7A6A5C"} />
          ),
        }}
      />
    </Tabs>
  );
}