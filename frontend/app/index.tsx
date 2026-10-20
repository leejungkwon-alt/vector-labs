import { useEffect } from "react";
import { ActivityIndicator, View, Text } from "react-native";
import { router } from "expo-router";
import { useAuthStore } from "@/store/authStore";
import { useProfileStore } from "@/store/profileStore";

export default function Index() {
  const ready = useAuthStore((s) => s.ready);
  const profileReady = useProfileStore((s) => s.ready);
  const profile = useProfileStore((s) => s.profile);

  useEffect(() => {
    if (!ready || !profileReady) return;
    router.replace(profile ? "/(tabs)/home" : "/birth-input");
  }, [ready, profileReady, profile]);

  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#FDF6EE" }}>
      <Text style={{ fontSize: 36, fontWeight: "800", color: "#E85D2F", marginBottom: 8, letterSpacing: 1 }}>Gyeol</Text>
      <ActivityIndicator color="#E85D2F" />
      <Text style={{ marginTop: 12, color: "#7A6A5C", fontSize: 14 }}>Reading the grain of your life...</Text>
    </View>
  );
}
