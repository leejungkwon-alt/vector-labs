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

// 자기신고 MBTI 선택 UI (선택 입력 · 건너뛰기 가능). 서버가 추정하지 않는다.
const MBTI_AXES = [
  { key: "EI", options: ["E", "I"] },
  { key: "NS", options: ["N", "S"] },
  { key: "TF", options: ["T", "F"] },
  { key: "JP", options: ["J", "P"] },
] as const;

type MbtiDraft = { EI: string | null; NS: string | null; TF: string | null; JP: string | null };

function toMbtiType(draft: MbtiDraft): string | null {
  const v = `${draft.EI ?? ""}${draft.NS ?? ""}${draft.TF ?? ""}${draft.JP ?? ""}`;
  return /^[EI][NS][TF][JP]$/.test(v) ? v : null;
}

/** 공백 제거 후 "5:3" → "05:03" 처럼 보정한다(수동 입력 대비). */
function normalizeClock(s: string): string {
  const m = s.trim().match(/^(\d{1,2})\s*:\s*(\d{1,2})$/);
  if (!m) return s.trim();
  return `${m[1].padStart(2, "0")}:${m[2].padStart(2, "0")}`;
}

/**
 * 저장된 프로필 → 화면 초기값.
 * 우선순위: 저장된 값 > 화면 기본값.
 * "시간 모름"으로 저장된 프로필(mode=noon/day_only 또는 time 없음)은 스위치를 켠 채로
 * 복원한다 → 사용자가 아무것도 바꾸지 않고 저장만 눌러도 시간이 되살아나지 않는다.
 */
export function deriveInitialForm(profile: any): { birth_date?: string; birth_time: string | null; unknown: boolean } {
  const out: { birth_date?: string; birth_time: string | null; unknown: boolean } = {
    birth_time: null,
    unknown: false,
  };
  if (!profile) return out;
  if (typeof profile.birth_date === "string" && /^\d{4}-\d{2}-\d{2}$/.test(profile.birth_date)) {
    out.birth_date = profile.birth_date;
  }
  const mode = typeof profile.birth_time_mode === "string" ? profile.birth_time_mode : null;
  if (mode === "noon" || mode === "day_only" || !profile.birth_time) {
    out.unknown = true;
  } else {
    out.birth_time = normalizeClock(String(profile.birth_time));
    out.unknown = false;
  }
  return out;
}

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

  // MBTI (선택). touched=false 면 payload 에 넣지 않아 기존 값이 보존된다.
  const [mbtiDraft, setMbtiDraft] = useState<MbtiDraft>({ EI: null, NS: null, TF: null, JP: null });
  const [mbtiTouched, setMbtiTouched] = useState(false);
  const [mbtiSkip, setMbtiSkip] = useState(false);
  // 저장된 MBTI 가 있으면 펼친 상태로 시작, 없으면 접힌 한 줄로 시작.
  const [mbtiExpanded, setMbtiExpanded] = useState(
    () => typeof profile?.mbti === "string" && /^[EI][NS][TF][JP]$/.test(profile.mbti)
  );
  const mbtiDraftValue = toMbtiType(mbtiDraft);


  // 🌟 직접 입력(Custom)을 위한 상태 추가
  const [isCustomCity, setIsCustomCity] = useState(false);
  const [customCityName, setCustomCityName] = useState(""); 
  const [customLongitude, setCustomLongitude] = useState(""); // 유저가 직접 입력할 경도
  const [customTimezone, setCustomTimezone] = useState("Asia/Seoul");
  const [showTimezoneModal, setShowTimezoneModal] = useState(false);

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
    : (CITIES.find(c => c.key === city)?.label || t("birthInput.cityDefault"));
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

      // 저장된 MBTI 가 있으면 4축 토글을 그 값으로 채운다 (없으면 미입력 = 건너뜀)
      if (typeof profile.mbti === "string" && /^[EI][NS][TF][JP]$/.test(profile.mbti)) {
        setMbtiDraft({
          EI: profile.mbti[0], NS: profile.mbti[1], TF: profile.mbti[2], JP: profile.mbti[3],
        });
        setMbtiSkip(false);
        setMbtiExpanded(true);   // 이미 고른 값이 있으면 접어두지 않는다
      }
      
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
      // 시간 모름 = noon + birth_time null (엔진의 "정오 가정" 규칙과 일치).
      //   - 이 화면은 "최초 입력"과 "설정 → 생년월일 재설정" 양쪽에서 열린다.
      //   - 프리필은 저장된 프로필 값을 화면 상태로 채운 것이고, 사용자가 그 상태로
      //     저장을 누르면 화면 상태가 곧 최종값이다(화면 = 미리 채워진 원본).
      //   - 따라서 세 필드를 **항상** 보낸다. (birth_time_mode 컬럼이 없던 시절의 API 는
      //     이 값을 저장조차 못 했고, birth_date/birth_time_mode 를 빼고 보내면 PUT 전체 교체
      //     특성상 저장된 birth_time 이 NULL 로 지워졌다.)
      const timeMode = unknownTime ? "noon" : "exact";
      let timeString: string | null = null;
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
            const msg = t("birthInput.longitudeInvalid");
            if (Platform.OS === "web") alert(msg); else Alert.alert(t("common.notice"), msg);
            return;
          }
          finalLongitude = parsedLon;
        } else {
          // 비워뒀으면 선택한 타임존의 대표 도시 경도 사용 (예전에는 타임존과 무관하게 서울 경도가 들어갔다)
          const d = defaultLongitudeForTimezone(customTimezone, birthDate);
          if (d === null) {
            const msg = t("birthInput.longitudeInvalid");
            if (Platform.OS === "web") alert(msg); else Alert.alert(t("common.notice"), msg);
            return;
          }
          finalLongitude = d;
        }
      } else {
        // 프리셋 도시: 서버가 birth_location 키로 정확한 값을 따로 해석한다 (여기 값은 참고용)
        finalLongitude = CITIES.find(c => c.key === city)?.longitude || 126.978;
      }

      const profileData: any = {
        birth_date: `${yyyy}-${mm}-${dd}`,
        birth_time: timeString,
        birth_time_mode: timeMode,
        birth_location: isCustomCity ? null : city,
        timezone_str: isCustomCity ? customTimezone : (CITIES.find(c => c.key === city)?.timezone || "Asia/Seoul"),
        longitude: finalLongitude, // 🌟 수정된 경도 적용
        gender: gender,
      };

      // MBTI: 사용자가 실제로 만졌을 때만 포함한다.
      //   - 4축 모두 선택 → 유형 문자열
      //   - 일부만 선택/건너뛰기 → null(미입력)
      //   - 건드리지 않음 → 키 생략 → 서버가 기존 값 유지
      if (mbtiTouched) {
        profileData.mbti = mbtiDraftValue; // null 이면 서버에서 "미입력"으로 저장
      }

      await saveProfile(profileData);
      router.replace("/(tabs)/home");
    } catch (error: any) {
      // 저장 실패: 화면을 넘기지 않고 그대로 머문다(입력값 보존). 서버 오류는 그대로 노출.
      const msg = error?.detail || error?.message || t("birthInput.saveFailed");
      if (Platform.OS === "web") alert(msg);
      else Alert.alert(t("common.notice"), msg);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: insets.bottom + 24 }}>
      <Text style={styles.title}>{t("birthInput.title")}</Text>
      {/*
        저장 payload 는 화면 상태에서 그대로 만든다(프리필 값도 사용자가 확인/수정할 수 있는
        "현재 값"이므로 우선순위는 항상 화면 상태 = 최종값이다).
        birth_date / birth_time / birth_time_mode 를 항상 보내야 전체 교체(PUT)에서
        기존 저장값이 지워지지 않는다.
        MBTI 는 "사용자가 실제로 건드렸을 때만" payload 에 넣어
        구버전/미변경 사용자의 기존 값을 지우지 않도록 한다.
      */}
      
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
          <Text style={styles.label}>{t("birthInput.cityNameLabel")}</Text>
          <TextInput
            style={styles.textInput}
            value={customCityName}
            onChangeText={(v) => { setCustomCityName(v); lookup.search(v); }}
            placeholder={t("birthInput.cityPlaceholder")}
            placeholderTextColor={colors.textMuted}
            autoCorrect={false}
          />
          {lookup.status === "loading" && <Text style={styles.hint}>{t("birthInput.cityLookupLoading")}</Text>}
          {lookup.status === "notfound" && <Text style={styles.hint}>{t("birthInput.cityLookupNotFound")}</Text>}
          {lookup.status === "error" && <Text style={styles.hint}>{t("birthInput.cityLookupError")}</Text>}
          {lookup.hits.length > 1 && lookup.hits.map((h, i) => (
            <TouchableOpacity key={i} onPress={() => applyHit(h)} style={styles.hitRow}>
              <Text style={styles.inputText}>{hitLabel(h)}</Text>
            </TouchableOpacity>
          ))}

          <Text style={[styles.label, { marginTop: 12 }]}>{t("birthInput.longitudeLabel")}</Text>
          <TextInput
            style={styles.textInput}
            value={customLongitude}
            onChangeText={setCustomLongitude}
            keyboardType={Platform.OS === "ios" ? "numbers-and-punctuation" : "numeric"}
            placeholder={t("birthInput.longitudePlaceholder")}
            placeholderTextColor={colors.textMuted}
          />
          <Text style={{ fontSize: 12, color: colors.textMuted, marginTop: 4, marginBottom: 12 }}>
            {t("birthInput.longitudeHint")}
          </Text>

          <Text style={styles.label}>{t("birthInput.birthTimezone")}</Text>
          <TouchableOpacity style={styles.textInput} onPress={() => setShowTimezoneModal(true)}>
            <Text style={{ fontSize: 15, color: colors.text }}>{tzLabel}</Text>
          </TouchableOpacity>
          <Text style={{ fontSize: 12, color: colors.textMuted, marginTop: 4 }}>
            {t("birthInput.timezoneHint")}
          </Text>
          {offsetLabel && (
            <Text style={styles.hint}>{t("birthInput.tzOffsetAtBirth")}: {offsetLabel}</Text>
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

      {/* ---- MBTI (선택 입력 · 컴팩트) ----
          기본은 접힌 한 줄. 이미 값이 있으면 펼친 상태로 시작한다.
          서버는 MBTI 를 추정하지 않고, 사용자가 고른 값만 저장한다. */}
      {!mbtiExpanded ? (
        <TouchableOpacity
          style={styles.mbtiCollapsedRow}
          onPress={() => setMbtiExpanded(true)}
          accessibilityRole="button"
          accessibilityLabel={t("birthInput.mbtiAdd")}
        >
          <Text style={styles.mbtiCollapsedText}>{t("birthInput.mbtiAdd")}</Text>
          <Text style={styles.mbtiChevron}>▾</Text>
        </TouchableOpacity>
      ) : (
        <View style={styles.mbtiBox}>
          <View style={styles.mbtiHeaderRow}>
            <Text style={styles.mbtiLabelInline}>{t("birthInput.mbtiLabel")}</Text>
            <TouchableOpacity onPress={() => setMbtiExpanded(false)} accessibilityRole="button">
              <Text style={styles.mbtiCollapseText}>▴ {t("common.close")}</Text>
            </TouchableOpacity>
          </View>

          <Text style={styles.mbtiHintInline}>{t("birthInput.mbtiHintShort")}</Text>

          {/* 한 줄에 4축(E|I, N|S, T|F, J|P). 축 이름 라벨은 표시하지 않는다. */}
          <View style={styles.mbtiAxisRow}>
            {MBTI_AXES.map((axis, idx) => (
              <View key={axis.key} style={[styles.mbtiAxisGroup, idx > 0 && styles.mbtiAxisGroupGap]}>
                {axis.options.map((opt) => {
                  const selected = mbtiDraft[axis.key] === opt;
                  return (
                    <TouchableOpacity
                      key={opt}
                      style={[styles.mbtiAxisBtn, selected && styles.mbtiAxisBtnActive]}
                      onPress={() => {
                        setMbtiTouched(true);
                        setMbtiDraft((prev) => ({ ...prev, [axis.key]: prev[axis.key] === opt ? null : opt }));
                      }}
                      accessibilityRole="button"
                      accessibilityState={{ selected }}
                    >
                      <Text style={[styles.mbtiAxisText, selected && styles.mbtiAxisTextActive]}>{opt}</Text>
                    </TouchableOpacity>
                  );
                })}
              </View>
            ))}
          </View>

          {/* 건너뛰기는 작은 텍스트 링크 */}
          <View style={styles.mbtiFooterRow}>
            <TouchableOpacity
              onPress={() => {
                setMbtiTouched(true);
                setMbtiDraft({ EI: null, NS: null, TF: null, JP: null });
                setMbtiSkip(true);
              }}
              accessibilityRole="button"
            >
              <Text style={styles.mbtiSkipLink}>
                {mbtiSkip ? "✓ " : ""}{t("birthInput.mbtiSkip")}
              </Text>
            </TouchableOpacity>
            <Text style={styles.mbtiSummary}>
              {mbtiDraftValue ? `${t("birthInput.mbtiSelected")}: ${mbtiDraftValue}` : ""}
            </Text>
          </View>
        </View>
      )}

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
  // ---- MBTI 컴팩트 UI ----
  mbtiCollapsedRow: {
    flexDirection: "row", alignItems: "center", justifyContent: "space-between",
    paddingVertical: 12, paddingHorizontal: 14, borderRadius: radius.md,
    backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border,
    borderStyle: "dashed", marginBottom: spacing.md,
  },
  mbtiCollapsedText: { fontSize: 14, fontWeight: "600", color: colors.primary },
  mbtiChevron: { fontSize: 12, color: colors.primary },
  mbtiBox: {
    backgroundColor: colors.surface, padding: 12, borderRadius: radius.md,
    borderWidth: 1, borderColor: colors.border, marginBottom: spacing.md,
  },
  mbtiHeaderRow: {
    flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: 2,
  },
  mbtiLabelInline: { fontSize: 13, fontWeight: "600", color: colors.textMuted },
  mbtiCollapseText: { fontSize: 12, color: colors.textMuted },
  mbtiHintInline: { fontSize: 12, color: colors.textMuted, marginTop: 4, marginBottom: 8 },
  mbtiAxisRow: { flexDirection: "row", alignItems: "center" },
  mbtiAxisGroup: { flex: 1, flexDirection: "row", gap: 4 },
  mbtiAxisGroupGap: { marginLeft: 6 },
  mbtiAxisBtn: {
    flex: 1, height: 36, justifyContent: "center", alignItems: "center",
    borderRadius: radius.sm, backgroundColor: colors.bg,
    borderWidth: 1, borderColor: colors.border,
  },
  mbtiAxisBtnActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  mbtiAxisText: { fontSize: 14, color: colors.textMuted },
  mbtiAxisTextActive: { color: colors.onPrimary, fontWeight: "700" },
  mbtiFooterRow: {
    flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginTop: 8,
  },
  mbtiSkipLink: { fontSize: 12, color: colors.primary, textDecorationLine: "underline" },
  mbtiSummary: { fontSize: 12, color: colors.textMuted },
  nextBtn: { backgroundColor: colors.primary, padding: 16, borderRadius: radius.md, alignItems: "center", marginTop: spacing.sm },
  nextBtnText: { fontSize: 17, fontWeight: "700", color: colors.onPrimary },
});