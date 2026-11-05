import { useEffect, useRef, useState } from "react";
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Switch, Alert, Platform, TextInput } from "react-native";
import { router } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useProfileStore } from "@/store/profileStore";
import { useLanguageStore } from "@/store/languageStore";
import { useT, formatPickerDate, formatPickerTime } from "@/i18n";
import { DateTimeField } from "@/components/DateTimeField";
import { CityPickerModal, CUSTOM_CITY_KEY } from "@/components/CityPickerModal";
import { TimezonePickerModal } from "@/components/TimezonePickerModal";
import { CITY_LIST } from "@/constants/cities";
import { TIMEZONE_LIST } from "@/constants/timezones";
import { colors, spacing, radius } from "@/theme";
import { useCityLookup } from "@/hooks/useCityLookup";
import {
  hitLabel, tzOffsetLabel, defaultLongitudeForTimezone, isLongitudeConsistent, CityHit,
} from "@/utils/cityLookup";

// CITY_LIST 에 longitude/timezone 이 없어도 동작하도록 느슨한 타입으로 사용
const CITIES = CITY_LIST as ReadonlyArray<{ key: string; label: string; longitude?: number; timezone?: string }>;

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

  // 🌟 직접 입력(Custom)을 위한 상태 추가
  const [isCustomCity, setIsCustomCity] = useState(false);
  const [customCityName, setCustomCityName] = useState(""); 
  const [customLongitude, setCustomLongitude] = useState(""); // 유저가 직접 입력할 경도
  const [customTimezone, setCustomTimezone] = useState("Asia/Seoul");
  const [showTimezoneModal, setShowTimezoneModal] = useState(false);

  // t() 가 키를 못 찾으면 키 문자열을 그대로 돌려주므로, 그 경우 기본 문구를 쓴다
  const tf = (key: string, fallback: string) => {
    const v = t(key);
    return !v || v === key ? fallback : v;
  };

  // 🌍 도시 이름 -> 경도 + 타임존 자동 조회
  const lookup = useCityLookup(lang);
  const applyHit = (h: CityHit) => {
    setCustomLongitude(String(Math.round(h.longitude * 1000) / 1000));
    setCustomTimezone(h.timezone); // 선택 목록에 없는 타임존이어도 tzLabel 이 원문을 그대로 보여준다
  };
  // 첫 번째 결과를 자동 적용 (동명 도시가 여럿이면 아래 후보 목록에서 바꿀 수 있다)
  useEffect(() => {
    if (lookup.status === "found" && lookup.hits[0]) applyHit(lookup.hits[0]);
  }, [lookup.hits]);

  const parseLongitude = (raw: string) => {
    const s = raw.trim().replace(",", ".");
    return s === "" ? NaN : Number(s);
  };

  // 🌟 UI에 표시할 도시 이름 (직접 입력이면 유저가 쓴 이름, 아니면 리스트 라벨)
  const cityLabel = isCustomCity 
    ? (customCityName || t("birthInput.customCity")) 
    : (CITIES.find(c => c.key === city)?.label || "서울 (Seoul)");
  const tzLabel = TIMEZONE_LIST.find(t => t.key === customTimezone)?.label || customTimezone;
  const offsetLabel = tzOffsetLabel(customTimezone, birthDate); // 출생일 시점의 UTC 오프셋 (역사·서머타임 반영)

  // 저장된 프로필이 있으면 그 값으로 입력칸 채우기
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
        if (profile.longitude) setCustomLongitude(String(profile.longitude));
      }
    } catch {
      /* 기본값으로 진행 */
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
      
      // 🌟 경도(Longitude)
      let finalLongitude = 126.978; // 기본값 (서울)
      if (isCustomCity) {
        if (customLongitude.trim() !== "") {
          const parsedLon = parseLongitude(customLongitude);
          if (!Number.isFinite(parsedLon) || Math.abs(parsedLon) > 180) {
            const msg = tf("birthInput.longitudeInvalid", "경도는 -180 ~ 180 사이의 숫자로 입력해 주세요.");
            if (Platform.OS === "web") alert(msg); else Alert.alert(t("common.notice"), msg);
            return;
          }
          finalLongitude = parsedLon;
        } else {
          // 비워뒀으면 선택한 타임존의 대표 도시 경도 사용 (예전에는 타임존과 무관하게 서울 경도가 들어갔다)
          const d = defaultLongitudeForTimezone(customTimezone, birthDate);
          if (d === null) {
            const msg = tf("birthInput.longitudeInvalid", "경도는 -180 ~ 180 사이의 숫자로 입력해 주세요.");
            if (Platform.OS === "web") alert(msg); else Alert.alert(t("common.notice"), msg);
            return;
          }
          finalLongitude = d;
        }
      } else {
        // 프리셋 도시: 서버가 birth_location 키로 정확한 값을 따로 해석한다 (여기 값은 참고용)
        finalLongitude = CITIES.find(c => c.key === city)?.longitude || 126.978;
      }

      const profileData = {
        birth_date: `${yyyy}-${mm}-${dd}`,
        birth_time: timeString,
        birth_time_mode: timeMode,
        birth_location: isCustomCity ? null : city,
        timezone_str: isCustomCity ? customTimezone : (CITIES.find(c => c.key === city)?.timezone || "Asia/Seoul"),
        longitude: finalLongitude, // 🌟 수정된 경도 적용
        gender: gender,
      };
      
      await saveProfile(profileData);
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

      {/* 🌟 직접 입력(Custom) UI 확장 */}
      {isCustomCity && (
        <View style={styles.customBox}>
          <Text style={styles.label}>도시 이름 (City Name)</Text>
          <TextInput
            style={styles.textInput}
            value={customCityName}
            onChangeText={(v) => { setCustomCityName(v); lookup.search(v); }}
            placeholder="예: 부산, 뉴욕"
            placeholderTextColor={colors.textMuted}
            autoCorrect={false}
          />
          {lookup.status === "loading" && <Text style={styles.hint}>{tf("birthInput.cityLookupLoading", "도시를 찾는 중…")}</Text>}
          {lookup.status === "notfound" && <Text style={styles.hint}>{tf("birthInput.cityLookupNotFound", "도시를 찾지 못했어요. 철자를 확인하거나 경도와 타임존을 직접 입력해 주세요.")}</Text>}
          {lookup.status === "error" && <Text style={styles.hint}>{tf("birthInput.cityLookupError", "도시 검색에 실패했어요. 경도와 타임존을 직접 입력해 주세요.")}</Text>}
          {lookup.hits.length > 1 && lookup.hits.map((h, i) => (
            <TouchableOpacity key={i} onPress={() => applyHit(h)} style={styles.hitRow}>
              <Text style={styles.inputText}>{hitLabel(h)}</Text>
            </TouchableOpacity>
          ))}

          <Text style={[styles.label, { marginTop: 12 }]}>경도 (Longitude)</Text>
          <TextInput
            style={styles.textInput}
            value={customLongitude}
            onChangeText={setCustomLongitude}
            keyboardType={Platform.OS === "ios" ? "numbers-and-punctuation" : "numeric"}
            placeholder="모르면 비워두세요 (타임존 대표 도시 경도 사용)"
            placeholderTextColor={colors.textMuted}
          />
          <Text style={{ fontSize: 12, color: colors.textMuted, marginTop: 4, marginBottom: 12 }}>
            * 사주 계산 시 태양시 보정에 사용됩니다. 모르시면 비워두셔도 됩니다.
          </Text>

          <Text style={styles.label}>{t("birthInput.birthTimezone")}</Text>
          <TouchableOpacity style={styles.textInput} onPress={() => setShowTimezoneModal(true)}>
            <Text style={{ fontSize: 15, color: colors.text }}>{tzLabel}</Text>
          </TouchableOpacity>
          <Text style={{ fontSize: 12, color: colors.textMuted, marginTop: 4 }}>
            {t("birthInput.timezoneHint")}
          </Text>
          {offsetLabel && (
            <Text style={styles.hint}>{tf("birthInput.tzOffsetAtBirth", "출생일 기준 UTC 오프셋")}: {offsetLabel}</Text>
          )}
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
      <TimezonePickerModal
        visible={showTimezoneModal}
        onClose={() => setShowTimezoneModal(false)}
        onSelect={(tz) => {
          setCustomTimezone(tz);
          // 이미 넣은 경도가 새 타임존과 어울리면 그대로 둔다 (예: 부산 129.07 + Asia/Seoul).
          // 비어 있거나 어울리지 않으면(예: 부산 경도 + 뉴욕 타임존) 새 타임존의 대표 도시 경도로 바꾼다.
          const cur = parseLongitude(customLongitude);
          if (!Number.isFinite(cur) || !isLongitudeConsistent(cur, tz, birthDate)) {
            const d = defaultLongitudeForTimezone(tz, birthDate);
            if (d !== null) setCustomLongitude(String(d));
          }
        }}
        currentTz={customTimezone}
      />
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
  customBox: { backgroundColor: colors.surface, padding: 16, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, marginBottom: spacing.md, marginTop: -8 },
  hint: { fontSize: 12, color: colors.textMuted, marginTop: 4 },
  hitRow: { paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: colors.border },
  textInput: { backgroundColor: colors.bg, padding: 12, borderRadius: radius.sm, borderWidth: 1, borderColor: colors.border, justifyContent: "center", minHeight: 44, color: colors.text },
  genderBtn: { flex: 1, padding: 14, borderRadius: radius.md, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, alignItems: "center" },
  genderBtnActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  genderText: { fontSize: 15, color: colors.textMuted },
  genderTextActive: { color: colors.onPrimary, fontWeight: "600" },
  nextBtn: { backgroundColor: colors.primary, padding: 16, borderRadius: radius.md, alignItems: "center", marginTop: spacing.sm },
  nextBtnText: { fontSize: 17, fontWeight: "700", color: colors.onPrimary },
});