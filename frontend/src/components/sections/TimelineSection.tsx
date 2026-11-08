// frontend/src/components/sections/TimelineSection.tsx
import { View, Text, Platform, TouchableOpacity, StyleSheet } from "react-native";
import { useState } from "react";
import { colors, gradeColors } from "@/theme";
import { ss } from "./shared";
import { useT } from "@/i18n";
import type { TimelineSection } from "../../../types";

export function TimelineSectionView({ section }: { section: TimelineSection }) {
  const t = useT();
  return (
    <View>

      {/* 인생 궤적 그라데이션 범례 */}
      <View style={{ marginBottom: 16 }}>
        <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 6 }}>
          <Text style={{ fontSize: 11, color: colors.textMuted, letterSpacing: 0.8, fontWeight: "600" }}>
            Challenging
          </Text>
          <Text style={{ fontSize: 11, color: colors.textMuted, letterSpacing: 0.8, fontWeight: "600" }}>
            Peak
          </Text>
        </View>
        <View style={{ height: 8, borderRadius: 4, overflow: "hidden" }}>
          {Platform.OS === "web" ? (
            <div
              style={{
                width: "100%",
                height: "100%",
                background:
                  "linear-gradient(to right, #EF4444 0%, #F97316 25%, #EAB308 50%, #22C55E 75%, #A855F7 100%)",
              }}
            />
          ) : (
            <View style={{ flexDirection: "row", flex: 1 }}>
              {["#EF4444", "#F97316", "#EAB308", "#22C55E", "#A855F7"].map((c, i) => (
                <View key={i} style={{ flex: 1, backgroundColor: c }} />
              ))}
            </View>
          )}
        </View>
      </View>
      {section.hero && <Text style={ss.coreHero}>{section.hero}</Text>}
      {section.items.map((item, i) => (
        <TimelineItem key={i} item={item} gradeColors={gradeColors} colors={colors} ss={ss} t={t} />
      ))}
    </View>
  );
}

function TimelineItem({ item, gradeColors, colors, ss, t }: any) {
  const [open, setOpen] = useState(item.is_current === true);
  const hasDetails = !!(item.theme || item.body || item.caution || item.practice);

  return (
    <View
      style={[
        ss.blockBox,
        item.is_current && { borderColor: colors.primary, borderWidth: 2 },
        { paddingVertical: 8 },
      ]}
    >
      <TouchableOpacity
        onPress={() => hasDetails && setOpen(!open)}
        disabled={!hasDetails}
        style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingVertical: 4 }}
      >
        <View style={{ flex: 1 }}>
          <Text style={{ fontSize: 15, fontWeight: "700", color: colors.text }}>
            {item.ages[0]}–{item.ages[1]}{t("sections.yearsOld")}
            {item.pillar_name ? ` · ${item.pillar_name}` : ""}
            {item.is_current && <Text style={{ color: colors.primary }}> · {t("sections.current")}</Text>}
          </Text>
          {item.theme && (
            <Text style={{ fontSize: 13, color: colors.textMuted, marginTop: 2 }}>
              {item.theme}
            </Text>
          )}
        </View>
        <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
          <Text style={{ fontSize: 13, fontWeight: "700", color: gradeColors[item.grade] || colors.text }}>
            {item.grade}
          </Text>
          {hasDetails && (
            <Text style={{ fontSize: 12, color: colors.textMuted }}>{open ? "▲" : "▼"}</Text>
          )}
        </View>
      </TouchableOpacity>

      {open && hasDetails && (
        <View style={{ marginTop: 10, paddingTop: 10, borderTopWidth: 1, borderTopColor: colors.border }}>
          {item.body && <Text style={[ss.paragraph, { marginBottom: 8 }]}>{item.body}</Text>}
          {item.caution && (
            <Text style={{ fontSize: 13, color: colors.warn, marginBottom: 6 }}>
              ⚠️ {item.caution}
            </Text>
          )}
          {item.practice && (
            <Text style={{ fontSize: 13, color: colors.primary }}>
              💡 {item.practice}
            </Text>
          )}
        </View>
      )}
    </View>
  );
}
