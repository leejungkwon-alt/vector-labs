// frontend/src/components/sections/LuckyCodeSection.tsx
import { View, Text } from "react-native";
import { colors } from "@/theme";
import { ss } from "./shared";
import { useT } from "@/i18n";
import type { LuckyCodeSection } from "../../../types";

export function LuckyCodeSectionView({ section }: { section: LuckyCodeSection }) {
  const t = useT();
  const p = section.power;
  const s = section.support;
  const watchOut = section.watch_out || [];

  return (
    <View>
      <Text style={ss.coreHero}>{section.hero}</Text>

      <View style={ss.blockBox}>
        <Text style={ss.blockTitle}>{t("sections.powerElement")} · {p.element}</Text>
        {p.colors && p.colors.length > 0 && (
          <Text style={ss.paragraph}>🎨 {t("sections.colors")}: {p.colors.join(", ")}</Text>
        )}
        {p.numbers && p.numbers.length > 0 && (
          <Text style={ss.paragraph}>🔢 {t("sections.numbers")}: {p.numbers.join(", ")}</Text>
        )}
        {p.directions && p.directions.length > 0 && (
          <Text style={ss.paragraph}>🧭 {t("sections.directions")}: {p.directions.join(", ")}</Text>
        )}
        {p.activities && p.activities.length > 0 && (
          <Text style={ss.paragraph}>🏃 {t("sections.activities")}: {p.activities.join(", ")}</Text>
        )}
        {p.foods && p.foods.length > 0 && (
          <Text style={ss.paragraph}>🍃 {t("sections.foods")}: {p.foods.join(", ")}</Text>
        )}
        {p.practices && p.practices.length > 0 && (
          <View style={{ marginTop: 6 }}>
            <Text style={[ss.metaText, { fontWeight: "700" }]}>{t("sections.practices")}</Text>
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
          <Text style={ss.blockTitle}>{t("sections.supportElement")} · {s.element}</Text>
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
          <Text style={[ss.blockTitle, { color: colors.danger }]}>{t("sections.watchOutLabel")}</Text>
          <Text style={ss.paragraph}>{watchOut.map(w => w.name).join(", ")}</Text>
        </View>
      )}
    </View>
  );
}
