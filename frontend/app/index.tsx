import { useEffect, useState } from "react";
import { ActivityIndicator, View, Text, TouchableOpacity } from "react-native";
import { router } from "expo-router";
import { useAuthStore } from "@/store/authStore";
import { useProfileStore } from "@/store/profileStore";

export default function Index() {
  const ready = useAuthStore((s) => s.ready);
  const profileReady = useProfileStore((s) => s.ready);
  const profile = useProfileStore((s) => s.profile);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    if (!ready || !profileReady) return;
    let mounted = true;
    const timeoutId = setTimeout(() => { if (mounted) setHasError(true); }, 4000);

    if (profile) router.replace("/(tabs)/home");
    else router.replace("/birth-input");

    if (mounted) clearTimeout(timeoutId);
    return () => { mounted = false; clearTimeout(timeoutId); };
  }, [ready, profileReady, profile]);

  if (hasError) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#FDF6EE", padding: 24 }}>
        <Text style={{ fontSize: 20, fontWeight: "700", color: "#C2461F", marginBottom: 12 }}>서버 연결 실패</Text>
        <TouchableOpacity style={{ backgroundColor: "#E85D2F", padding: 16, borderRadius: 12 }} onPress={() => router.replace("/birth-input")}>
          <Text style={{ color: "#FFF", fontWeight: "700", fontSize: 16 }}>화면 보기</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#FDF6EE" }}>
      <Text style={{ fontSize: 32, fontWeight: "700", color: "#E85D2F", marginBottom: 16 }}>SAJU</Text>
      <ActivityIndicator color="#E85D2F" />
      <Text style={{ marginTop: 12, color: "#7A6A5C" }}>Preparing your session...</Text>
    </View>
  );
}
