import { createElement, useState } from "react";
import { Platform, Text, TouchableOpacity, View } from "react-native";
import type { StyleProp, TextStyle, ViewStyle } from "react-native";
import DateTimePicker, { DateTimePickerEvent } from "@react-native-community/datetimepicker";

// 👇 우리가 만든 휠 피커를 불러옵니다. (같은 components 폴더에 있으므로 ./ 로 시작)
import BirthDateWheelPicker from "./BirthDateWheelPicker";

/**
 * 웹(텔레그램 미니앱)에서도 동작하는 날짜/시간 입력 필드.
 *  - 웹: 글자 위에 투명한 <input type="date|time"> 을 덮어, 탭하면 브라우저/텔레그램의 기본 선택기가 열린다.
 *  - 앱(iOS/Android): 
 *    - 날짜(mode="date")는 우리가 커스텀한 BirthDateWheelPicker(휠)를 띄운다.
 *    - 시간(mode="time")은 기존처럼 @react-native-community/datetimepicker (spinner) 를 사용한다.
 */
type Props = {
  mode: "date" | "time";
  value: Date;
  onChange: (next: Date) => void;
  displayText: string;
  disabled?: boolean;
  style?: StyleProp<ViewStyle>;
  textStyle?: StyleProp<TextStyle>;
};

const pad = (n: number, w = 2) => String(n).padStart(w, "0");
const dateStr = (d: Date) => `${pad(d.getFullYear(), 4)}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
const timeStr = (d: Date) => `${pad(d.getHours())}:${pad(d.getMinutes())}`;
const MIN_DATE = "1900-01-01";

export function DateTimeField({ mode, value, onChange, displayText, disabled, style, textStyle }: Props) {
  const [showNative, setShowNative] = useState(false); // 시간(Time) 선택용 기존 달력
  const [showWheel, setShowWheel] = useState(false);   // 날짜(Date) 선택용 커스텀 휠

  if (Platform.OS === "web") {
    const handleChange = (e: any) => {
      const v = String(e?.target?.value ?? "");
      if (!v) return;
      if (mode === "date") {
        const [y, m, d] = v.split("-").map(Number);
        if (!y || !m || !d || y < 1900) return; // 직접 타이핑 중인 미완성 연도 무시
        onChange(new Date(y, m - 1, d));
      } else {
        const [h, mi] = v.split(":").map(Number);
        if (Number.isNaN(h) || Number.isNaN(mi)) return;
        onChange(new Date(2000, 0, 1, h, mi));
      }
    };

    return (
      <View style={[style, { position: "relative" }, disabled && { opacity: 0.4 }]}>
        <Text style={textStyle}>{displayText}</Text>
        {createElement("input", {
          type: mode,
          value: mode === "date" ? dateStr(value) : timeStr(value),
          min: mode === "date" ? MIN_DATE : undefined,
          max: mode === "date" ? dateStr(new Date()) : undefined,
          disabled,
          "aria-label": displayText,
          onChange: handleChange,
          onClick: (e: any) => {
            if (disabled) return;
            try {
              e.currentTarget.showPicker?.(); // 데스크톱 크롬/엣지: 클릭 시 달력 팝업
            } catch {
              /* 일부 브라우저는 지원하지 않음 — 기본 동작에 맡김 */
            }
          },
          style: {
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            opacity: 0,
            cursor: disabled ? "default" : "pointer",
            border: 0,
            padding: 0,
            margin: 0,
            fontSize: 16,
            boxSizing: "border-box",
            background: "transparent",
          },
        })}
      </View>
    );
  }

  // 앱(iOS / Android) 환경일 때
  return (
    <>
      <TouchableOpacity
        style={[style, disabled && { opacity: 0.4 }]}
        disabled={disabled}
        onPress={() => {
          if (mode === "date") {
            setShowWheel(true); // 👈 날짜 선택 시 커스텀 휠 피커 열기
          } else {
            setShowNative(true); // 👈 시간 선택 시 기존 스피너 열기
          }
        }}
      >
        <Text style={textStyle}>{displayText}</Text>
      </TouchableOpacity>

      {/* 1. 날짜 선택용 커스텀 휠 피커 */}
      {showWheel && (
        <BirthDateWheelPicker
          visible={showWheel}
          initialDate={dateStr(value)} // Date 객체를 "YYYY-MM-DD" 문자열로 변환해서 전달
          onClose={() => setShowWheel(false)}
          onConfirm={(dateString) => {
            // "YYYY-MM-DD" 형태의 문자열을 다시 Date 객체로 변환하여 부모 컴포넌트에 전달
            const [y, m, d] = dateString.split("-").map(Number);
            onChange(new Date(y, m - 1, d));
          }}
        />
      )}

      {/* 2. 시간 선택용 기존 달력 (안드로이드 기본 제공) */}
      {showNative && mode === "time" && (
        <DateTimePicker
          value={value}
          mode="time"
          display="spinner"
          onChange={(event: DateTimePickerEvent, d?: Date) => {
            setShowNative(false);
            if (event.type === "set" && d) onChange(d);
          }}
        />
      )}
    </>
  );
}