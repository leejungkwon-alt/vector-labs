// frontend/src/components/sections/LuckyCodeSection.tsx
import { View, Text } from "react-native";
import { colors } from "@/theme";
import { ss } from "./shared";
import type { LuckyCodeSection } from "../../../types";

export function LuckyCodeSectionView({ section }: { section: LuckyCodeSection }) {
  const p = section.power;
  const s = section.support;
  const watchOut = section.watch_out || [];

  return (
    <View>
      <Text style={ss.coreHero}>{section.hero}</Text>

      <View style={ss.blockBox}>
        <Text style={ss.blockTitle}>핵심 기운 · {p.element}</Text>
        {p.colors && p.colors.length > 0 && (
          <Text style={ss.paragraph}>🎨 색상: {p.colors.join(", ")}</Text>
        )}
        {p.numbers && p.numbers.length > 0 && (
          <Text style={ss.paragraph}>🔢 숫자: {p.numbers.join(", ")}</Text>
        )}
        {p.directions && p.directions.length > 0 && (
          <Text style={ss.paragraph}>🧭 방위: {p.directions.join(", ")}</Text>
        )}
        {p.activities && p.activities.length > 0 && (
          <Text style={ss.paragraph}>🏃 활동: {p.activities.join(", ")}</Text>
        )}
        {p.foods && p.foods.length > 0 && (
          <Text style={ss.paragraph}>🍃 음식: {p.foods.join(", ")}</Text>
        )}
        {p.practices && p.practices.length > 0 && (
          <View style={{ marginTop: 6 }}>
            <Text style={[ss.metaText, { fontWeight: "700" }]}>실천</Text>
            {p.practices.map((pr, i) => (
              <Text key={i} style={ss.paragraph}>• {pr}</Text>
            ))}
          </View>
        )}
        {p.keywords.length > 0 && (
          <View style={ss.tagRow}>
            {p.keywords.map((k, i) => (
              <Text key={i} style={ss.tag}>#{k}</Text>
            ))}
          </View>
        )}
      </View>

      {s && (
        <View style={ss.blockBox}>
          <Text style={ss.blockTitle}>보조 기운 · {s.element}</Text>
          {s.colors && s.colors.length > 0 && (
            <Text style={ss.paragraph}>🎨 {s.colors.join(", ")}</Text>
          )}
          {s.numbers && s.numbers.length > 0 && (
            <Text style={ss.paragraph}>🔢 {s.numbers.join(", ")}</Text>
          )}
          {s.directions && s.directions.length > 0 && (
            <Text style={ss.paragraph}>🧭 {s.directions.join(", ")}</Text>
          )}
        </View>
      )}

      {watchOut.length > 0 && (
        <View style={[ss.blockBox, { backgroundColor: colors.dangerSoft, borderColor: colors.danger }]}>
          <Text style={[ss.blockTitle, { color: colors.danger }]}>주의</Text>
          <Text style={ss.paragraph}>{watchOut.map(w => w.name).join(", ")}</Text>
        </View>
      )}
    </View>
  );
}
