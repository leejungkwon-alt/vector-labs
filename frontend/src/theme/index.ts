// frontend/src/theme/index.ts

export const colors = {
  // ---- Base surfaces ----
  bg: "#FDF6EE",
  bgElevated: "#F9F6F0",
  bgMuted: "#F0EAE1",
  surface: "#FFFFFF",

  // ---- Text ----
  text: "#2B1B12",
  textMuted: "#7A6A5C",
  onPrimary: "#FFFFFF",

  // ---- Brand ----
  primary: "#E85D2F",
  primarySoft: "#FDEFEA",

  // ---- Borders ----
  border: "#EADFCF",

  // ---- Semantic ----
  danger: "#C2461F",
  dangerSoft: "#FFF5F0",
  success: "#2F7A3F",
  successSoft: "#E8F4EB",
  warn: "#D4A017",
  warnSoft: "#FDF6E3",
} as const;

// 등급 색상 — compatibility / daily / timeline 공통
export const gradeColors: Record<string, string> = {
  PEAK: colors.success,
  FAVORABLE: "#5FAF7A",
  NEUTRAL: colors.textMuted,
  CAUTION: colors.warn,
  CHALLENGING: colors.danger,
};

export const spacing = { xs: 4, sm: 8, md: 16, lg: 24, xl: 32 } as const;
export const radius = { sm: 8, md: 12, lg: 20, pill: 999 } as const;

export const shadow = {
  sm: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  md: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 2,
  },
} as const;
