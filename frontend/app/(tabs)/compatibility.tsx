import { useLanguageStore } from "@/store/languageStore"; // SAJU-PATCH:api-lang
import { useT } from "@/i18n";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, ActivityIndicator, Switch } from "react-native";
import DateTimePicker, { DateTimePickerEvent } from "@react-native-community/datetimepicker";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { router } from "expo-router";
import { api, ApiError } from "@/api/client";
import { colors, spacing, radius, gradeColors } from "@/theme";
import { useProfileStore } from "@/store/profileStore";
import { CityPickerModal, CUSTOM_CITY_KEY } from "@/components/CityPickerModal";
import { TimezonePickerModal } from "@/components/TimezonePickerModal";
import { PaymentModal } from "@/components/PaymentModal";
import { CITY_LIST } from "@/constants/cities";
import { TIMEZONE_LIST } from "@/constants/timezones";

export default function CompatibilityScreen() {
  const lang = useLanguageStore((s) => s.lang); // SAJU-PATCH:lang-decl
  const t = useT();
  const insets = useSafeAreaInsets();
  const myProfile = useProfileStore((s) => s.profile);

  const [relationshipType, setRelationshipType] = useState<"romance" | "business" | "friend" | "family">("romance");
  const [showPayment, setShowPayment] = useState(false);

  const [partnerDate, setPartnerDate] = useState(new Date(1995, 9, 24));
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [partnerTime, setPartnerTime] = useState(new Date(2000, 0, 1, 12, 0));
  const [showTimePicker, setShowTimePicker] = useState(false);
  const [unknownTime, setUnknownTime] = useState(true);
  
  const [city, setCity] = useState("seoul");
  const [showCityModal, setShowCityModal] = useState(false);
  const [gender, setGender] = useState("F");

  const [isCustomCity, setIsCustomCity] = useState(false);
  const [customTimezone, setCustomTimezone] = useState("Asia/Seoul");
  const [showTimezoneModal, setShowTimezoneModal] = useState(false);

  const [isCalculated, setIsCalculated] = useState(false);
  const cityLabel = isCustomCity ? t("birthInput.customCity") : (CITY_LIST.find(c => c.key === city)?.label || "서울 (Seoul)");
  const tzLabel = TIMEZONE_LIST.find(t => t.key === customTimezone)?.label || customTimezone;

  const onSelectCity = (key: string) => {
    if (key === CUSTOM_CITY_KEY) {
      setIsCustomCity(true);
    } else {
      setIsCustomCity(false);
      setCity(key);
    }
  };

  const onChangeDate = (event: DateTimePickerEvent, date?: Date) => {
    setShowDatePicker(false);
    if (event.type === "set" && date) setPartnerDate(date);
  };

  const onChangeTime = (event: DateTimePickerEvent, time?: Date) => {
    setShowTimePicker(false);
    if (event.type === "set" && time) setPartnerTime(time);
  };

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["compatibility", relationshipType, lang],
    queryFn: async () => {
      if (!myProfile) throw new Error("내 사주 정보가 없습니다. 홈에서 먼저 입력해주세요.");

      const yyyy = partnerDate.getFullYear();
      const mm = String(partnerDate.getMonth() + 1).padStart(2, "0");
      const dd = String(partnerDate.getDate()).padStart(2, "0");
      const timeMode = unknownTime ? "noon" : "exact";
      let timeString = null;
      if (!unknownTime) {
        const hh = String(partnerTime.getHours()).padStart(2, "0");
        const min = String(partnerTime.getMinutes()).padStart(2, "0");
        timeString = `${hh}:${min}:00`;
      }

      const offsetHours = new Date().getTimezoneOffset() / -60; 
      const fallbackLongitude = 0 /* FIX-22: backend handles timezone */;

      return api.compatibility({
        person_a: myProfile,
        person_b: {
          birth_date: `${yyyy}-${mm}-${dd}`,
          birth_time: timeString,
          birth_time_mode: timeMode,
          birth_location: isCustomCity ? null : city,
          timezone_str: isCustomCity ? customTimezone : "Asia/Seoul",
          longitude: isCustomCity ? fallbackLongitude : 126.978,
          gender: gender as "M" | "F",
        },
        relationship_type: relationshipType,
        lang,
      });
    },
    enabled: false,
  });

  const handleCalculate = async () => {
    if (!myProfile) return;
    setIsCalculated(true);
    await refetch();
  };

  const renderResult = () => {
    if (isLoading) return <ActivityIndicator size="large" color={colors.primary} style={{ marginTop: 20 }} />;
    if (error) {
      const msg = error instanceof ApiError ? error.detail : (error as Error).message;
      
      // 👇 403 에러(궁합 결제 필요)일 때 예쁜 결제 유도 화면 노출
      if (error instanceof ApiError && error.status === 403) {
        return (
          <View style={{ marginTop: 30, padding: 24, backgroundColor: colors.primary + "10", borderRadius: radius.lg, alignItems: "center", borderWidth: 1, borderColor: colors.primary + "30" }}>
            <Text style={{ fontSize: 40, marginBottom: 12 }}>💎</Text>
            <Text style={{ fontSize: 20, fontWeight: "800", color: colors.text, marginBottom: 8 }}>{t("compatibility.paywallTitle")}</Text>
            <Text style={{ fontSize: 15, color: colors.textMuted, textAlign: "center", marginBottom: 24, lineHeight: 22 }}>
              {t("compatibility.paywallBody")}
            </Text>
            <TouchableOpacity 
              style={{ backgroundColor: colors.primary, paddingHorizontal: 24, paddingVertical: 16, borderRadius: radius.md, width: "100%", alignItems: "center" }} 
              onPress={() => setShowPayment(true)}
            >
              <Text style={{ color: "#FFF", fontSize: 16, fontWeight: "700" }}>{t("compatibility.paywallCta")}</Text>
            </TouchableOpacity>
          </View>
        );
      }
      
      // 그 외 일반 에러
      return <Text style={{ color: colors.danger, marginTop: 20, textAlign: "center" }}>{msg}</Text>;
    }
    if (!data?.compatibility) return null;
    const compat = data.compatibility;
    
    // 👇 -1.0 ~ 1.0 점수를 0 ~ 100점으로 직관적 변환
    const rawScore = compat.overall.score;
    const displayScore = Math.round((rawScore + 1) * 50);
    
    const color = gradeColors[compat.overall.grade] || colors.text;

    return (
      <View style={{ marginTop: 30, gap: 16 }}>
        <View style={styles.resultCard}>
          <Text style={styles.resultLabel}>
            {relationshipType === "romance" ? t("compatibility.resultRomance") : 
             relationshipType === "business" ? t("compatibility.resultBusiness") : 
             relationshipType === "friend" ? t("compatibility.resultFriend") : t("compatibility.resultFamily")}
          </Text>
          
          {/* 👇 100점 만점 점수 표시 및 게이지 바 */}
          <View style={{ flexDirection: "row", alignItems: "flex-end", marginBottom: 8 }}>
            <Text style={[styles.overallScore, { color }]}>{displayScore}</Text>
            <Text style={{ fontSize: 20, fontWeight: "700", color: colors.textMuted, marginBottom: 10 }}> / 100 {t("compatibility.scoreUnit")}</Text>
          </View>
          
          <View style={styles.gaugeBg}>
            <View style={[styles.gaugeFill, { width: `${displayScore}%`, backgroundColor: color }]} />
          </View>
          
          <Text style={[styles.overallGrade, { color }]}>{compat.overall.grade_label}</Text>
          <Text style={styles.resultHeadline}>{compat.overall.headline}</Text>
          <Text style={styles.resultBody}>{compat.overall.body}</Text>
        </View>

        {compat.relationship_advice && (
          <View style={styles.tipCard}>
            <Text style={styles.tipTitle}>{t("compatibility.adviceTitle")}</Text>
            <Text style={styles.tipBody}>{compat.relationship_advice}</Text>
          </View>
        )}

        {Object.entries(compat.axes).map(([key, axis]) => (
          <View key={key} style={styles.axisCard}>
            <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 8 }}>
              <Text style={styles.axisTitle}>
                {key === "elements" ? t("compatibility.axisElements") : key === "day_master" ? t("compatibility.axisDayMaster") : key === "ten_gods" ? t("compatibility.axisTenGods") : t("compatibility.axisSinsal")}
              </Text>
              <Text style={{ fontWeight: "700", color: gradeColors[axis.grade] }}>{axis.grade}</Text>
            </View>
            <Text style={{ fontSize: 16, fontWeight: "600", color: colors.text, marginBottom: 4 }}>{axis.headline}</Text>
            <Text style={{ fontSize: 14, color: colors.textMuted, lineHeight: 20 }}>{axis.body}</Text>
          </View>
        ))}
      </View>
    );
  };

  if (!myProfile) {
    return (
      <View style={[styles.container, { justifyContent: "center", alignItems: "center" }]}>
        <Text style={{ color: colors.textMuted }}>{t("compatibility.noProfile")}</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: insets.bottom + 40 }}>
      <Text style={styles.title}>{t("compatibility.title")}</Text>

      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 24 }}>
        <View style={[styles.segmentWrap, { paddingRight: 0 }]}>
          {[
            { key: "romance", label: t("compatibility.typeRomance") },
            { key: "business", label: t("compatibility.typeBusiness") },
            { key: "friend", label: t("compatibility.typeFriend") },
            { key: "family", label: t("compatibility.typeFamily") },
          ].map((tab) => (
            <TouchableOpacity 
              key={tab.key}
              style={[styles.segmentBtn, relationshipType === tab.key && styles.segmentBtnActive, { paddingHorizontal: 16 }]} 
              onPress={() => setRelationshipType(tab.key as any)}
            >
              <Text style={[styles.segmentText, relationshipType === tab.key && styles.segmentTextActive]}>{tab.label}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>

      <Text style={styles.label}>{t("compatibility.partnerDate")}</Text>
      <TouchableOpacity style={styles.inputBtn} onPress={() => setShowDatePicker(true)}>
        <Text style={styles.inputText}>{partnerDate.getFullYear()}년 {partnerDate.getMonth() + 1}월 {partnerDate.getDate()}일</Text>
      </TouchableOpacity>
      {showDatePicker && <DateTimePicker value={partnerDate} mode="date" display="spinner" onChange={onChangeDate} />}

      <View style={styles.rowBetween}>
        <Text style={styles.label}>{t("compatibility.partnerTime")}</Text>
        <View style={styles.switchWrap}>
          <Text style={{ fontSize: 13, color: colors.textMuted, marginRight: 6 }}>{t("compatibility.unknownTime")}</Text>
          <Switch value={unknownTime} onValueChange={setUnknownTime} trackColor={{ false: colors.border, true: colors.primary }} />
        </View>
      </View>

      <TouchableOpacity style={[styles.inputBtn, unknownTime && { opacity: 0.4, backgroundColor: colors.bgMuted }]} onPress={() => { if(!unknownTime) setShowTimePicker(true); }} disabled={unknownTime}>
        <Text style={styles.inputText}>
          {unknownTime ? t("compatibility.timeUnknown") : `${String(partnerTime.getHours()).padStart(2, "0")}:${String(partnerTime.getMinutes()).padStart(2, "0")}`}
        </Text>
      </TouchableOpacity>
      {showTimePicker && <DateTimePicker value={partnerTime} mode="time" display="spinner" onChange={onChangeTime} />}

      <Text style={styles.label}>{t("compatibility.partnerCity")}</Text>
      <TouchableOpacity style={styles.inputBtn} onPress={() => setShowCityModal(true)}>
        <Text style={styles.inputText}>{cityLabel}</Text>
      </TouchableOpacity>

      {isCustomCity && (
        <View style={styles.customBox}>
          <Text style={styles.label}>{t("compatibility.partnerTimezone")}</Text>
          <TouchableOpacity style={styles.textInput} onPress={() => setShowTimezoneModal(true)}>
            <Text style={{ fontSize: 15, color: colors.text }}>{tzLabel}</Text>
          </TouchableOpacity>
        </View>
      )}

      <Text style={styles.label}>{t("compatibility.partnerGender")}</Text>
      <View style={{ flexDirection: "row", gap: 10, marginBottom: 24 }}>
        <TouchableOpacity style={[styles.genderBtn, gender === "M" && styles.genderBtnActive]} onPress={() => setGender("M")}>
          <Text style={[styles.genderText, gender === "M" && styles.genderTextActive]}>{t("compatibility.male")}</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.genderBtn, gender === "F" && styles.genderBtnActive]} onPress={() => setGender("F")}>
          <Text style={[styles.genderText, gender === "F" && styles.genderTextActive]}>{t("compatibility.female")}</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity
        style={[styles.nextBtn, !myProfile && { opacity: 0.4 }]}
        onPress={handleCalculate}
        disabled={!myProfile}
      >
        <Text style={styles.nextBtnText}>{t("compatibility.calculate")}</Text>
      </TouchableOpacity>

      {isCalculated && renderResult()}

      <CityPickerModal visible={showCityModal} onClose={() => setShowCityModal(false)} onSelect={onSelectCity} currentCityKey={isCustomCity ? CUSTOM_CITY_KEY : city} />
      <TimezonePickerModal visible={showTimezoneModal} onClose={() => setShowTimezoneModal(false)} onSelect={setCustomTimezone} currentTz={customTimezone} />
      <PaymentModal visible={showPayment} onClose={() => setShowPayment(false)} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg, padding: spacing.lg },
  title: { fontSize: 20, fontWeight: "700", color: colors.text, marginBottom: 16, marginTop: 10 },
  
  segmentWrap: { flexDirection: "row", backgroundColor: colors.surface, borderRadius: radius.pill, padding: 4, marginBottom: 24, borderWidth: 1, borderColor: colors.border },
  segmentBtn: { flex: 1, paddingVertical: 12, alignItems: "center", borderRadius: radius.pill },
  segmentBtnActive: { backgroundColor: colors.primary },
  segmentText: { fontSize: 15, fontWeight: "600", color: colors.textMuted },
  segmentTextActive: { color: colors.onPrimary, fontWeight: "700" },

  label: { fontSize: 15, fontWeight: "600", color: colors.textMuted, marginBottom: 6 },
  rowBetween: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 6 },
  switchWrap: { flexDirection: "row", alignItems: "center" },
  inputBtn: { backgroundColor: colors.surface, padding: 14, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, marginBottom: 16 },
  inputText: { fontSize: 15, color: colors.text },
  customBox: { backgroundColor: colors.surface, padding: 14, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, marginBottom: 16, marginTop: -8 },
  textInput: { backgroundColor: colors.bg, padding: 10, borderRadius: radius.sm, borderWidth: 1, borderColor: colors.border, justifyContent: "center", minHeight: 40 },
  genderBtn: { flex: 1, padding: 14, borderRadius: radius.md, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, alignItems: "center" },
  genderBtnActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  genderText: { fontSize: 15, color: colors.textMuted },
  genderTextActive: { color: colors.onPrimary, fontWeight: "600" },
  nextBtn: { backgroundColor: colors.primary, padding: 16, borderRadius: radius.md, alignItems: "center" },
  nextBtnText: { fontSize: 17, fontWeight: "700", color: colors.onPrimary },
  
  resultCard: { backgroundColor: colors.surface, padding: spacing.xl, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, alignItems: "center" },
  resultLabel: { fontSize: 14, fontWeight: "700", color: colors.textMuted, marginBottom: 8 },
  
  // 👇 100점 만점 스타일
  overallScore: { fontSize: 56, fontWeight: "800" },
  gaugeBg: { width: "100%", height: 8, backgroundColor: colors.bgMuted, borderRadius: 4, marginBottom: 16, overflow: "hidden" },
  gaugeFill: { height: "100%", borderRadius: 4 },
  
  overallGrade: { fontSize: 20, fontWeight: "700", marginBottom: 16 },
  resultHeadline: { fontSize: 18, fontWeight: "700", color: colors.text, textAlign: "center", marginBottom: 8 },
  resultBody: { fontSize: 15, color: colors.textMuted, textAlign: "center", lineHeight: 22 },
  
  tipCard: { backgroundColor: colors.primary + "10", padding: spacing.md, borderRadius: radius.md, borderWidth: 1, borderColor: colors.primary + "30" },
  tipTitle: { fontSize: 14, fontWeight: "700", color: colors.primary, marginBottom: 6 },
  tipBody: { fontSize: 15, color: colors.text, lineHeight: 22 },

  axisCard: { backgroundColor: colors.surface, padding: spacing.md, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border },
  axisTitle: { fontSize: 14, fontWeight: "700", color: colors.primary },
});
