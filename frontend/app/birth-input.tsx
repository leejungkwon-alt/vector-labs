import { useEffect, useRef, useState } from "react";
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Switch, Alert, Platform } from "react-native";
import { router } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useProfileStore } from "@/store/profileStore";
import { useLanguageStore } from "@/store/languageStore";
import { useT, formatPickerDate, formatPickerTime } from "@/i18n";
import { DateTimeField } from "@/components/DateTimeField";
import { CityPickerModal, CUSTOM_CITY_KEY } from "@/components/CityPickerModal";
import { TimezonePickerModal } from "@/components/TimezonePickerModal"; // 👈 추가
import { CITY_LIST } from "@/constants/cities";
import { TIMEZONE_LIST } from "@/constants/timezones";
import { colors, spacing, radius } from "@/theme";

export default function BirthInput() {
  const insets = useSafeAreaInsets();
  const saveProfile = useProfileStore((s) => s.saveProfile);
  const profile = useProfileStore((s) => s.profile);
  const lang = useLanguageStore((s) => s.lang);
  const t = useT();
  
  const [birthDate, setBirthDate] = useState(new Date(1990, 0, 1));
  const [birthTime, setBirthTime] = useState(new Date(2000, 0, 1, 12, 0));
  const [unknownTime, setUnknownTime] = useState(false);
  
  const [city, setCity] = useState("seoul");
  const [showCityModal, setShowCityModal] = useState(false);
  const [gender, setGender] = useState("M");

  const [isCustomCity, setIsCustomCity] = useState(false);
  const [customTimezone, setCustomTimezone] = useState("Asia/Seoul");
  const [showTimezoneModal, setShowTimezoneModal] = useState(false); // 👈 타임존 모달 상태

  const cityLabel = isCustomCity ? t("birthInput.customCity") : (CITY_LIST.find(c => c.key === city)?.label || "서울 (Seoul)");
  const tzLabel = TIMEZONE_LIST.find(t => t.key === customTimezone)?.label || customTimezone;

  // 저장된 프로필이 있으면(= 설정에서 "생년월일 수정"으로 들어온 경우) 그 값으로 입력칸을 채운다.
  const hydrated = useRef(false);
  useEffect(() => {
    if (hydrated.current || !profile) return;
    hydrated.current = true;
    try {
      if (profile.birth_date) {
        const [y, m, d] = String(profile.birth_date).split("-").map(Number);
        if (y && m && d) setBirthDate(new Date(y, m - 1, d));
      }
      if (profile.birth_time_mode === "noon" || !profile.birth_time) {
        setUnknownTime(true);
      } else {
        const [hh, mm] = String(profile.birth_time).split(":").map(Number);
        if (!Number.isNaN(hh) && !Number.isNaN(mm)) setBirthTime(new Date(2000, 0, 1, hh, mm));
        setUnknownTime(false);
      }
      if (profile.gender === "M" || profile.gender === "F") setGender(profile.gender);
      if (profile.birth_location) {
        setIsCustomCity(false);
        setCity(profile.birth_location);
      } else if (profile.timezone_str) {
        setIsCustomCity(true);
        setCustomTimezone(profile.timezone_str);
      }
    } catch {
      /* 프로필 형식이 예상과 달라도 기본값으로 진행 */
    }
  }, [profile]);

  const onSelectCity = (key: string) => {
    if (key === CUSTOM_CITY_KEY) {
      setIsCustomCity(true);
    } else {
      setIsCustomCity(false);
      setCity(key);
    }
  };

  const handleNext = async () => {
    try {
      const yyyy = birthDate.getFullYear();
      const mm = String(birthDate.getMonth() + 1).padStart(2, "0");
      const dd = String(birthDate.getDate()).padStart(2, "0");
      const timeMode = unknownTime ? "noon" : "exact";
      let timeString = null;
      if (!unknownTime) {
        const hh = String(birthTime.getHours()).padStart(2, "0");
        const min = String(birthTime.getMinutes()).padStart(2, "0");
        timeString = `${hh}:${min}:00`;
      }
      
      const offsetHours = new Date().getTimezoneOffset() / -60; 
      const fallbackLongitude = 0 ;

      const profile = {
        birth_date: `${yyyy}-${mm}-${dd}`,
        birth_time: timeString,
        birth_time_mode: timeMode,
        birth_location: isCustomCity ? null : city,
        timezone_str: isCustomCity ? customTimezone : "Asia/Seoul",
        longitude: isCustomCity ? fallbackLongitude : 126.978,
        gender: gender,
      };
      
      await saveProfile(profile);
      router.replace("/(tabs)/home");
    } catch (error) {
      if (Platform.OS === "web") alert(t("birthInput.saveFailed"));
      else Alert.alert(t("common.notice"), t("birthInput.saveFailed"));
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: insets.bottom + 24 }}>
      <Text style={styles.title}>{t("birthInput.title")}</Text>
      
      <Text style={styles.label}>{t("birthInput.birthDate")}</Text>
      <DateTimeField
        mode="date"
        value={birthDate}
        onChange={setBirthDate}
        displayText={formatPickerDate(birthDate, lang)}
        style={styles.inputBtn}
        textStyle={styles.inputText}
      />

      <View style={styles.rowBetween}>
        <Text style={styles.label}>{t("birthInput.birthTime")}</Text>
        <View style={styles.switchWrap}>
          <Text style={{ fontSize: 13, color: colors.textMuted, marginRight: 6 }}>{t("birthInput.unknownTime")}</Text>
          <Switch value={unknownTime} onValueChange={setUnknownTime} trackColor={{ false: colors.border, true: colors.primary }} />
        </View>
      </View>

      <DateTimeField
        mode="time"
        value={birthTime}
        onChange={setBirthTime}
        disabled={unknownTime}
        displayText={unknownTime ? t("birthInput.timeUnknown") : formatPickerTime(birthTime)}
        style={styles.inputBtn}
        textStyle={styles.inputText}
      />

      <Text style={styles.label}>{t("birthInput.birthCity")}</Text>
      <TouchableOpacity style={styles.inputBtn} onPress={() => setShowCityModal(true)}>
        <Text style={styles.inputText}>{cityLabel}</Text>
      </TouchableOpacity>

      {isCustomCity && (
        <View style={styles.customBox}>
          <Text style={styles.label}>{t("birthInput.birthTimezone")}</Text>
          {/* 👇 텍스트 입력 대신 터치하면 타임존 선택 모달이 뜨도록 변경 */}
          <TouchableOpacity style={styles.textInput} onPress={() => setShowTimezoneModal(true)}>
            <Text style={{ fontSize: 15, color: colors.text }}>{tzLabel}</Text>
          </TouchableOpacity>
          <Text style={{ fontSize: 12, color: colors.textMuted, marginTop: 4 }}>
            {t("birthInput.timezoneHint")}
          </Text>
        </View>
      )}

      <Text style={styles.label}>{t("birthInput.gender")}</Text>
      <View style={{ flexDirection: "row", gap: 10, marginBottom: 16 }}>
        <TouchableOpacity style={[styles.genderBtn, gender === "M" && styles.genderBtnActive]} onPress={() => setGender("M")}>
          <Text style={[styles.genderText, gender === "M" && styles.genderTextActive]}>{t("birthInput.male")}</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.genderBtn, gender === "F" && styles.genderBtnActive]} onPress={() => setGender("F")}>
          <Text style={[styles.genderText, gender === "F" && styles.genderTextActive]}>{t("birthInput.female")}</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.nextBtn} onPress={handleNext}>
        <Text style={styles.nextBtnText}>{t("birthInput.submit")}</Text>
      </TouchableOpacity>

      <CityPickerModal visible={showCityModal} onClose={() => setShowCityModal(false)} onSelect={onSelectCity} currentCityKey={isCustomCity ? CUSTOM_CITY_KEY : city} />
      <TimezonePickerModal visible={showTimezoneModal} onClose={() => setShowTimezoneModal(false)} onSelect={setCustomTimezone} currentTz={customTimezone} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg, padding: spacing.lg },
  title: { fontSize: 22, fontWeight: "700", color: colors.text, marginBottom: spacing.lg, marginTop: 10 },
  label: { fontSize: 15, fontWeight: "600", color: colors.textMuted, marginBottom: 6 },
  rowBetween: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 6 },
  switchWrap: { flexDirection: "row", alignItems: "center" },
  inputBtn: { backgroundColor: colors.surface, padding: 14, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, marginBottom: spacing.md },
  inputText: { fontSize: 15, color: colors.text },
  customBox: { backgroundColor: colors.surface, padding: 14, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, marginBottom: spacing.md, marginTop: -8 },
  textInput: { backgroundColor: colors.bg, padding: 10, borderRadius: radius.sm, borderWidth: 1, borderColor: colors.border, justifyContent: "center", minHeight: 40 },
  genderBtn: { flex: 1, padding: 14, borderRadius: radius.md, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, alignItems: "center" },
  genderBtnActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  genderText: { fontSize: 15, color: colors.textMuted },
  genderTextActive: { color: colors.onPrimary, fontWeight: "600" },
  nextBtn: { backgroundColor: colors.primary, padding: 16, borderRadius: radius.md, alignItems: "center", marginTop: spacing.sm },
  nextBtnText: { fontSize: 17, fontWeight: "700", color: colors.onPrimary },
});
