// frontend/src/components/DonutChart.tsx
import React from "react";
import { View, Text, StyleSheet } from "react-native";
import Svg, { Circle } from "react-native-svg";
import { colors } from "@/theme";

export const ELEMENT_COLORS: Record<string, string> = {
  "木": "#2F7A3F", // Growth (Green)
  "火": "#E85D2F", // Spark (Red)
  "土": "#D4A017", // Ground (Yellow)
  "金": "#9AACB8", // Edge (Gray)
  "水": "#1B3A5C", // Flow (Blue)
};

export function DonutChart({ data }: { data: Record<string, number> }) {
  const size = 180;
  const strokeWidth = 26;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  
  let accumulatedPercent = 0;

  return (
    <View style={styles.container}>
      <Svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* 배경 원 */}
        <Circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={colors.bgMuted}
          strokeWidth={strokeWidth}
          fill="none"
        />
        {/* 데이터 원들 */}
        {Object.entries(data).map(([elem, val]) => {
          if (val === 0) return null;
          
          const strokeDasharray = `${(val / 100) * circumference} ${circumference}`;
          const strokeDashoffset = -(accumulatedPercent / 100) * circumference;
          accumulatedPercent += val;

          return (
            <Circle
              key={elem}
              cx={size / 2}
              cy={size / 2}
              r={radius}
              stroke={ELEMENT_COLORS[elem] || colors.primary}
              strokeWidth={strokeWidth}
              strokeDasharray={strokeDasharray}
              strokeDashoffset={strokeDashoffset}
              fill="none"
              transform={`rotate(-90 ${size / 2} ${size / 2})`}
            />
          );
        })}
      </Svg>
      <View style={styles.centerText}>
        <Text style={styles.centerLabel}>에너지</Text>
        <Text style={styles.centerValue}>분포</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: "center",
    justifyContent: "center",
    marginVertical: 16,
  },
  centerText: {
    position: "absolute",
    alignItems: "center",
    justifyContent: "center",
  },
  centerLabel: {
    fontSize: 13,
    color: colors.textMuted,
    marginBottom: 2,
  },
  centerValue: {
    fontSize: 18,
    fontWeight: "700",
    color: colors.text,
  },
});
