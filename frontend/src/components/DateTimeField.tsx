import { createElement, useState } from "react";
import { Platform, Text, TouchableOpacity, View } from "react-native";
import type { StyleProp, TextStyle, ViewStyle } from "react-native";
import DateTimePicker, { DateTimePickerEvent } from "@react-native-community/datetimepicker";

/**
 * 웹(텔레그램 미니앱)에서도 동작하는 날짜/시간 입력 필드.
 *  - 웹: 글자 위에 투명한 <input type="date|time"> 을 덮어, 탭하면 브라우저/텔레그램의 기본 선택기가 열린다.
 *  - 앱(iOS/Android): 기존처럼 @react-native-community/datetimepicker (spinner) 를 사용한다.
 *    (이 라이브러리는 웹을 지원하지 않아 웹에서는 아무것도 뜨지 않았다.)
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
  const [showNative, setShowNative] = useState(false);

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
          mode={mode}
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
