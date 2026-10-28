// frontend/src/components/CrisisBanner.tsx
// SAJU-COMPLIANCE: 자살예방/위기 리소스 배너. App Store 5.1.1 / Play 정책 대응.
import { View, Text, TouchableOpacity, Linking, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius } from "@/theme";
import { useLanguageStore } from "@/store/languageStore";
import { useT } from "@/i18n";

type CrisisResource = { hotline?: string; phone?: string; url?: string };

type Pack = { title: string; body: string; fallback: string; find: string };

const FALLBACKS: Record<string, Pack> = {
  ko: {
    title: "도움이 필요하시면",
    body: "위기 상황이라면 {hotline} ({phone})에 연락하세요.",
    fallback: "위기 상황이라면 지역 자살예방 핫라인에 연락하세요.",
    find: "지역별 핫라인 찾기",
  },
  en: {
    title: "If you need support",
    body: "In crisis, contact {hotline} ({phone}).",
    fallback: "If you are in crisis, contact a local suicide prevention hotline.",
    find: "Find a helpline",
  },
  ja: {
    title: "サポートが必要なとき",
    body: "危機的な状況なら {hotline}（{phone}）にご連絡ください。",
    fallback: "危機的な状況なら地域の自殺予防ホットラインにご連絡ください。",
    find: "地域のホットラインを探す",
  },
  zh_cn: {
    title: "如果您需要帮助",
    body: "如遇危机，请联系 {hotline}（{phone}）。",
    fallback: "如遇危机，请联系当地的自杀预防热线。",
    find: "查找当地热线",
  },
  es: {
    title: "Si necesitas apoyo",
    body: "En crisis, contacta {hotline} ({phone}).",
    fallback: "Si estás en crisis, contacta con una línea de prevención del suicidio local.",
    find: "Buscar una línea de ayuda",
  },
};

function pick(lang: string, key: keyof Pack): string {
  const pack = FALLBACKS[lang] ?? FALLBACKS.en;
  return pack[key];
}

export function CrisisBanner({ crisis }: { crisis?: CrisisResource }) {
  const lang = useLanguageStore((s) => s.lang);
  const t = useT();

  const tr = (key: string, fbKey: keyof Pack): string => {
    const fromI18n = t(`crisis.${key}`);
    if (!fromI18n || fromI18n === `crisis.${key}`) return pick(lang, fbKey);
    return fromI18n;
  };

  const phone = crisis?.phone;
  const hotline = crisis?.hotline;
  const url = crisis?.url || "https://findahelpline.com/";

  const title = tr("title", "title");
  const fallbackText = tr("fallback", "fallback");
  const findText = tr("findHelpline", "find");

  const bodyText =
    hotline && phone
      ? pick(lang, "body").replace("{hotline}", hotline).replace("{phone}", phone)
      : fallbackText;

  return (
    <View style={styles.box}>
      <View style={styles.header}>
        <Ionicons name="heart-circle" size={20} color="#8B1E1E" />
        <Text style={styles.title}>{title}</Text>
      </View>
      <Text style={styles.body}>{bodyText}</Text>
      {phone ? (
        <TouchableOpacity
          style={styles.callButton}
          onPress={() => Linking.openURL(`tel:${phone}`)}
        >
          <Ionicons name="call" size={16} color="#FFFFFF" />
          <Text style={styles.callButtonText}>{phone}</Text>
        </TouchableOpacity>
      ) : null}
      <TouchableOpacity
        style={styles.linkButton}
        onPress={() => Linking.openURL(url)}
      >
        <Text style={styles.linkText}>{findText}</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  box: {
    margin: spacing.lg,
    marginBottom: 0,
    padding: spacing.md,
    backgroundColor: "#FDF2F2",
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: "#F5C2C2",
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 8,
  },
  title: {
    fontSize: 14,
    fontWeight: "700",
    color: "#8B1E1E",
    marginLeft: 6,
  },
  body: {
    fontSize: 13,
    color: "#4A1A1A",
    lineHeight: 20,
    marginBottom: 10,
  },
  callButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#B91C1C",
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderRadius: radius.sm,
    marginBottom: 6,
  },
  callButtonText: {
    color: "#FFFFFF",
    fontWeight: "700",
    fontSize: 14,
    marginLeft: 6,
  },
  linkButton: {
    paddingVertical: 6,
    alignItems: "center",
  },
  linkText: {
    fontSize: 12,
    color: "#8B1E1E",
    textDecorationLine: "underline",
  },
});
