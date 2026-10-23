import { useState } from "react";
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Switch, Alert } from "react-native";
import { router } from "expo-router";
import DateTimePicker, { DateTimePickerEvent } from "@react-native-community/datetimepicker";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useProfileStore } from "@/store/profileStore";
import { CityPickerModal, CUSTOM_CITY_KEY } from "@/components/CityPickerModal";
import { TimezonePickerModal } from "@/components/TimezonePickerModal"; // 👈 추가
import { CITY_LIST } from "@/constants/cities";
import { TIMEZONE_LIST } from "@/constants/timezones";
import { colors, spacing, radius } from "@/theme";

export default function BirthInput() {
  const insets = useSafeAreaInsets();
  const saveProfile = useProfileStore((s) => s.saveProfile);
  
  const [birthDate, setBirthDate] = useState(new Date(1990, 0, 1));
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [birthTime, setBirthTime] = useState(new Date(2000, 0, 1, 12, 0));
  const [showTimePicker, setShowTimePicker] = useState(false);
  const [unknownTime, setUnknownTime] = useState(false);
  
  const [city, setCity] = useState("seoul");
  const [showCityModal, setShowCityModal] = useState(false);
  const [gender, setGender] = useState("M");

  const [isCustomCity, setIsCustomCity] = useState(false);
  const [customTimezone, setCustomTimezone] = useState("Asia/Seoul");
  const [showTimezoneModal, setShowTimezoneModal] = useState(false); // 👈 타임존 모달 상태

  const cityLabel = isCustomCity ? "직접 입력" : (CITY_LIST.find(c => c.key === city)?.label || "서울 (Seoul)");
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
    if (event.type === "set" && date) setBirthDate(date);
  };

  const onChangeTime = (event: DateTimePickerEvent, time?: Date) => {
    setShowTimePicker(false);
    if (event.type === "set" && time) setBirthTime(time);
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
      const fallbackLongitude = 0 /* FIX-22: backend handles timezone */;

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
      Alert.alert("오류", "저장에 실패했습니다. 입력값을 확인해주세요.");
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: insets.bottom + 24 }}>
      <Text style={styles.title}>출생 정보 입력</Text>
      
      <Text style={styles.label}>생년월일</Text>
      <TouchableOpacity style={styles.inputBtn} onPress={() => setShowDatePicker(true)}>
        <Text style={styles.inputText}>{birthDate.getFullYear()}년 {birthDate.getMonth() + 1}월 {birthDate.getDate()}일</Text>
      </TouchableOpacity>
      {showDatePicker && <DateTimePicker value={birthDate} mode="date" display="spinner" onChange={onChangeDate} />}

      <View style={styles.rowBetween}>
        <Text style={styles.label}>출생 시간</Text>
        <View style={styles.switchWrap}>
          <Text style={{ fontSize: 13, color: colors.textMuted, marginRight: 6 }}>시간을 몰라요</Text>
          <Switch value={unknownTime} onValueChange={setUnknownTime} trackColor={{ false: colors.border, true: colors.primary }} />
        </View>
      </View>

      <TouchableOpacity style={[styles.inputBtn, unknownTime && { opacity: 0.4 }]} onPress={() => { if(!unknownTime) setShowTimePicker(true); }} disabled={unknownTime}>
        <Text style={styles.inputText}>
          {unknownTime ? "시간 모름 (정오 기준)" : `${String(birthTime.getHours()).padStart(2, "0")}시 ${String(birthTime.getMinutes()).padStart(2, "0")}분`}
        </Text>
      </TouchableOpacity>
      {showTimePicker && <DateTimePicker value={birthTime} mode="time" display="spinner" onChange={onChangeTime} />}

      <Text style={styles.label}>출생지</Text>
      <TouchableOpacity style={styles.inputBtn} onPress={() => setShowCityModal(true)}>
        <Text style={styles.inputText}>{cityLabel}</Text>
      </TouchableOpacity>

      {isCustomCity && (
        <View style={styles.customBox}>
          <Text style={styles.label}>출생지 타임존 (Timezone)</Text>
          {/* 👇 텍스트 입력 대신 터치하면 타임존 선택 모달이 뜨도록 변경 */}
          <TouchableOpacity style={styles.textInput} onPress={() => setShowTimezoneModal(true)}>
            <Text style={{ fontSize: 15, color: colors.text }}>{tzLabel}</Text>
          </TouchableOpacity>
          <Text style={{ fontSize: 12, color: colors.textMuted, marginTop: 4 }}>
            * 정확한 경도는 시스템이 타임존을 기준으로 자동 계산합니다.
          </Text>
        </View>
      )}

      <Text style={styles.label}>성별</Text>
      <View style={{ flexDirection: "row", gap: 10, marginBottom: 16 }}>
        <TouchableOpacity style={[styles.genderBtn, gender === "M" && styles.genderBtnActive]} onPress={() => setGender("M")}>
          <Text style={[styles.genderText, gender === "M" && styles.genderTextActive]}>남성</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.genderBtn, gender === "F" && styles.genderBtnActive]} onPress={() => setGender("F")}>
          <Text style={[styles.genderText, gender === "F" && styles.genderTextActive]}>여성</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.nextBtn} onPress={handleNext}>
        <Text style={styles.nextBtnText}>결과 보기</Text>
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
