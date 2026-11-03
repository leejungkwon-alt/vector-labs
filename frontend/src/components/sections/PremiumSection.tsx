// frontend/src/components/sections/PremiumSection.tsx
import { View, Text } from "react-native";
import { colors, radius, spacing } from "@/theme";
import { ss, CompatBox, RedFlagsBox } from "./shared";
import { useT } from "@/i18n";
import type { PremiumSection, TimingBlock, TimingMonth, CrossInsightBlock } from "../../../types";

const LOCKED_LABELS: Record<string, string> = {
  cross_insight: "sections.lockedLabels.cross_insight",
  timing: "sections.lockedLabels.timing",
  body: "sections.lockedLabels.body",
  patterns: "sections.lockedLabels.patterns",
  compatibility: "sections.lockedLabels.compatibility",
  actions: "sections.lockedLabels.actions",
  action: "sections.lockedLabels.action",
  red_flags: "sections.lockedLabels.red_flags",
};

function LockedFieldsList({ fields }: { fields: string[] }) {
  const t = useT();
  if (!fields || fields.length === 0) return null;
  const labels = fields.map((f) => LOCKED_LABELS[f] ? t(LOCKED_LABELS[f]) : f);
  return (
    <View
      style={{
        marginTop: 12,
        padding: 12,
        backgroundColor: colors.bgElevated,
        borderRadius: radius.md,
        borderWidth: 1,
        borderColor: colors.border,
      }}
    >
      <Text style={{ fontSize: 12, fontWeight: "700", color: colors.textMuted }}>
        🔒 {t("sections.lockedContentCount", { count: fields.length })}
      </Text>
      <Text style={{ fontSize: 12, color: colors.textMuted, marginTop: 4, lineHeight: 18 }}>
        {labels.join(" · ")}
      </Text>
    </View>
  );
}

function MonthChip({ item, kind }: { item: TimingMonth; kind: "opportunity" | "caution" }) {
  const t = useT();
  const isOpp = kind === "opportunity";
  const tone = isOpp ? colors.success : colors.danger;
  const bg = isOpp ? colors.successSoft : colors.dangerSoft;
  const label = isOpp ? t("sections.opportunityMonth") : t("sections.cautionMonth");
  return (
    <View style={{ backgroundColor: bg, borderRadius: radius.md, padding: spacing.md, marginTop: spacing.sm, borderWidth: 1, borderColor: tone + "40" }}>
      <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 4, flexWrap: "wrap", gap: 4 }}>
        <Text style={{ fontSize: 13, fontWeight: "700", color: tone }}>{label} · {item.month}월</Text>
        <Text style={{ fontSize: 12, color: colors.textMuted, flexShrink: 1, textAlign: "right" }}>{item.grade_label}</Text>
      </View>
      <Text style={{ fontSize: 14, color: colors.text, lineHeight: 22 }}>{item.narrative}</Text>
    </View>
  );
}

function TimingBlockView({ timing }: { timing: TimingBlock }) {
  const t = useT();
  const dw = timing.daewoon;
  const yr = timing.year;
  return (
    <View style={{ backgroundColor: colors.bgElevated, borderRadius: radius.md, padding: spacing.md, marginTop: spacing.md, borderWidth: 1, borderColor: colors.border }}>
      <Text style={{ fontSize: 12, fontWeight: "700", color: colors.primary, letterSpacing: 1, marginBottom: spacing.sm }}>
        {t("sections.currentLifeFlow")}
      </Text>

      <View style={{ marginBottom: yr ? spacing.md : 0 }}>
        <View style={{ flexDirection: "row", alignItems: "center", gap: 6, marginBottom: 4, flexWrap: "wrap" }}>
          <Text style={{ fontSize: 13, fontWeight: "700", color: colors.text }}>{t("sections.currentDecade")}</Text>
          {dw.pillar ? (
            <Text style={{ fontSize: 12, color: colors.textMuted }}>
              {dw.ages?.[0]}–{dw.ages?.[1]}세 · {dw.pillar}{dw.grade_label ? ` · ${dw.grade_label}` : ""}
            </Text>
          ) : null}
        </View>
        <Text style={{ fontSize: 14, color: colors.text, lineHeight: 22 }}>{dw.narrative}</Text>
      </View>

      {yr ? (
        <View style={{ marginBottom: timing.opportunity_month || timing.caution_month ? spacing.md : 0 }}>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 6, marginBottom: 4, flexWrap: "wrap" }}>
            <Text style={{ fontSize: 13, fontWeight: "700", color: colors.text }}>{t("sections.thisYear")}</Text>
            <Text style={{ fontSize: 12, color: colors.textMuted }}>{yr.target_year} · {yr.ten_god_label}</Text>
          </View>
          <Text style={{ fontSize: 14, color: colors.text, lineHeight: 22 }}>{yr.narrative}</Text>
        </View>
      ) : null}

      {timing.opportunity_month ? <MonthChip item={timing.opportunity_month} kind="opportunity" /> : null}
      {timing.caution_month ? <MonthChip item={timing.caution_month} kind="caution" /> : null}

      {timing.disclaimer ? (
        <Text style={{ fontSize: 11, color: colors.textMuted, marginTop: spacing.sm, fontStyle: "italic", lineHeight: 16 }}>
          {timing.disclaimer}
        </Text>
      ) : null}
    </View>
  );
}

function CrossInsightBlockView({ block }: { block: CrossInsightBlock }) {
  return (
    <View
      style={{
        backgroundColor: colors.primarySoft,
        borderRadius: radius.md,
        padding: spacing.md,
        marginTop: spacing.md,
        borderWidth: 1,
        borderColor: colors.primary + "30",
      }}
    >
      <Text
        style={{
          fontSize: 12,
          fontWeight: "700",
          color: colors.primary,
          letterSpacing: 1,
          marginBottom: spacing.sm,
        }}
      >
        {"숨겨진 얼굴들"}
      </Text>
      <Text style={{ fontSize: 14, color: colors.text, lineHeight: 22, marginBottom: 6 }}>
        {block.intro}
      </Text>
      {block.tension_text ? (
        <Text style={{ fontSize: 14, color: colors.text, lineHeight: 22, marginBottom: 6 }}>
          {block.tension_text}
        </Text>
      ) : null}
      {block.angle ? (
        <Text style={{ fontSize: 14, color: colors.text, lineHeight: 22, marginBottom: 6 }}>
          {block.angle}
        </Text>
      ) : null}
      {block.closing ? (
        <Text style={{ fontSize: 13, color: colors.textMuted, lineHeight: 20, marginTop: 4 }}>
          {block.closing}
        </Text>
      ) : null}
      {block.disclaimer ? (
        <Text
          style={{
            fontSize: 11,
            color: colors.textMuted,
            marginTop: spacing.sm,
            fontStyle: "italic",
            lineHeight: 16,
          }}
        >
          {block.disclaimer}
        </Text>
      ) : null}
    </View>
  );
}

export function PremiumSectionView({ section }: { section: PremiumSection }) {
  const t = useT();
  return (
    <View>
      <Text style={ss.coreHero}>{section.headline}</Text>
      <Text style={ss.paragraph}>{section.body}</Text>

      {section.cross_insight ? (
        <CrossInsightBlockView block={section.cross_insight} />
      ) : null}

      {section.timing ? <TimingBlockView timing={section.timing} /> : null}

      {section.patterns && section.patterns.length > 0 ? (
        <View style={{ marginTop: 12 }}>
          <Text style={ss.blockTitle}>{t("sections.patterns")}</Text>
          {section.patterns.map((p, i) => (
            <Text key={i} style={ss.paragraph}>• {p}</Text>
          ))}
        </View>
      ) : null}

      {section.actions && section.actions.length > 0 ? (
        <View style={{ marginTop: 12 }}>
          <Text style={ss.blockTitle}>{t("sections.additionalActions")}</Text>
          {section.actions.map((a, i) => (
            <Text key={i} style={ss.paragraph}>→ {a}</Text>
          ))}
        </View>
      ) : null}

      {section.locked_fields && section.locked_fields.length > 0 ? (
        <LockedFieldsList fields={section.locked_fields} />
      ) : null}

      <CompatBox compat={section.compatibility} />
      <RedFlagsBox flags={section.red_flags} />
    </View>
  );
}