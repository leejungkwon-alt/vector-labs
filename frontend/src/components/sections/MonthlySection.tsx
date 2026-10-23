// frontend/src/components/sections/MonthlySection.tsx
import { View, Text } from "react-native";
import { colors, gradeColors } from "@/theme";
import { ss } from "./shared";
import type { MonthlySection } from "../../../types";

export function MonthlySectionView({ section }: { section: MonthlySection }) {
  return (
    <View>
      {section.hero && <Text style={ss.coreHero}>{section.hero}</Text>}
      {section.items.map((item, i) => (
        <View key={i} style={ss.blockBox}>
          <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 4, flexWrap: "wrap", gap: 4 }}>
            <Text style={{ fontSize: 15, fontWeight: "700", color: colors.text }}>
              {item.approx_solar_month} · {item.pillar}
            </Text>
            <Text
              style={{
                fontSize: 13,
                fontWeight: "700",
                color: gradeColors[item.grade] || colors.text,
              }}
            >
              {item.grade_label || item.grade}
            </Text>
          </View>
          <Text style={{ fontSize: 16, fontWeight: "600", color: colors.text, marginBottom: 4 }}>
            {item.name}
          </Text>
          <Text style={ss.paragraph}>{item.headline}</Text>
          {item.body && <Text style={ss.paragraph}>{item.body}</Text>}
          {item.grade_context && <Text style={ss.metaText}>{item.grade_context}</Text>}
          {(item.lean_into || item.watch_for) && (
            <View style={{ marginTop: 6 }}>
              {item.lean_into && <Text style={ss.metaText}>💡 집중: {item.lean_into}</Text>}
              {item.watch_for && <Text style={ss.metaText}>⚠️ 주의: {item.watch_for}</Text>}
            </View>
          )}
        </View>
      ))}
    </View>
  );
}
