import { Tabs } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "@/theme";

export default function TabsLayout() {
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
          title: "홈",
          tabBarIcon: ({ color }) => <Ionicons name="sunny-outline" size={24} color={color || "#7A6A5C"} />,
        }}
      />
      <Tabs.Screen
        name="daily"
        options={{
          title: "데일리",
          tabBarIcon: ({ color }) => <Ionicons name="calendar-outline" size={24} color={color || "#7A6A5C"} />,
        }}
      />
      {/* 👇 궁합 탭 추가 */}
      <Tabs.Screen
        name="compatibility"
        options={{
          title: "케미",
          tabBarIcon: ({ color }) => <Ionicons name="heart-outline" size={24} color={color || "#7A6A5C"} />,
        }}
      />
      <Tabs.Screen
        name="settings"
        options={{
          title: "설정",
          tabBarIcon: ({ color }) => <Ionicons name="settings-outline" size={24} color={color || "#7A6A5C"} />,
        }}
      />
    </Tabs>
  );
}
