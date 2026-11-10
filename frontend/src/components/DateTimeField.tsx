import { createElement, useState } from "react";
import { Platform, Text, TouchableOpacity, View } from "react-native";
import type { StyleProp, TextStyle, ViewStyle } from "react-native";
import DateTimePicker, { DateTimePickerEvent } from "@react-native-community/datetimepicker";

// 👇 커스텀 휠 피커 추가
import BirthDateWheelPicker from "./BirthDateWheelPicker";

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
  const [showNative, setShowNative] = useState(false);
  const [showWheel, setShowWheel] = useState(false);

  // =========================================================
  // 1. 날짜(mode="date") 선택: 웹/앱 상관없이 무조건 휠 피커 사용!
  // =========================================================
  if (mode === "date") {
    return (
      <>
        <TouchableOpacity
          style={[style, disabled && { opacity: 0.4 }]}
          disabled={disabled}
          onPress={() => {
            if (Platform.OS === "web") {
              // 텔레그램 웹뷰 터치 씹힘 방지: 포커스 해제 후 약간의 지연
              if (typeof document !== "undefined" && document.activeElement instanceof HTMLElement) {
                document.activeElement.blur();
              }
              setTimeout(() => setShowWheel(true), 50);
            } else {
              setShowWheel(true);
            }
          }}
        >
          <Text style={textStyle}>{displayText}</Text>
        </TouchableOpacity>

        {showWheel && (
          <BirthDateWheelPicker
            visible={showWheel}
            initialDate={dateStr(value)}
            onClose={() => setShowWheel(false)}
            onConfirm={(dateString) => {
              const [y, m, d] = dateString.split("-").map(Number);
              onChange(new Date(y, m - 1, d));
            }}
          />
        )}
      </>
    );
  }

  // =========================================================
  // 2. 시간(mode="time") 선택: 기존 로직 유지
  // =========================================================
  if (Platform.OS === "web") {
    const handleChange = (e: any) => {
      const v = String(e?.target?.value ?? "");
      if (!v) return;
      const [h, mi] = v.split(":").map(Number);
      if (Number.isNaN(h) || Number.isNaN(mi)) return;
      onChange(new Date(2000, 0, 1, h, mi));
    };

    return (
      <View style={[style, { position: "relative" }, disabled && { opacity: 0.4 }]}>
        <Text style={textStyle}>{displayText}</Text>
        {createElement("input", {
          type: "time",
          value: timeStr(value),
          disabled,
          "aria-label": displayText,
          onChange: handleChange,
          style: {
            position: "absolute", top: 0, left: 0, width: "100%", height: "100%",
            opacity: 0, cursor: disabled ? "default" : "pointer", border: 0, padding: 0, margin: 0,
          },
        })}
      </View>
    );
  }

  return (
    <>
      <TouchableOpacity
        style={[style, disabled && { opacity: 0.4 }]}
        disabled={disabled}
        onPress={() => setShowNative(true)}
      >
        <Text style={textStyle}>{displayText}</Text>
      </TouchableOpacity>
      {showNative && (
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