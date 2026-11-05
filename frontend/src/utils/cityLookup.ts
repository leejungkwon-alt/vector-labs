// frontend/src/utils/cityLookup.ts
// 도시 이름 -> 경도 / IANA 타임존 자동 조회 (Open-Meteo Geocoding API, 무료·API 키 불필요)
// React 의존성이 없는 순수 로직이라 테스트하기 쉽습니다. 화면에서는 useCityLookup 훅으로 사용합니다.

export type CityHit = {
  name: string;
  admin1?: string;   // 시/도, 주
  country?: string;
  latitude: number;
  longitude: number;
  timezone: string;  // 예: "Asia/Seoul"
};

const ENDPOINT = "https://geocoding-api.open-meteo.com/v1/search";

// 앱 언어 코드 -> Open-Meteo language 파라미터
const LANG_MAP: Record<string, string> = { ko: "ko", en: "en", ja: "ja", zh_cn: "zh", es: "es" };

export function isValidTimezone(tz: unknown): tz is string {
  if (typeof tz !== "string" || !tz) return false;
  try {
    new Intl.DateTimeFormat("en-US", { timeZone: tz });
    return true;
  } catch {
    return false;
  }
}

/** 응답 한 줄을 검증해서 쓸 수 있는 것만 CityHit 으로 변환 (이상한 값은 버림) */
export function toHit(r: any): CityHit | null {
  if (!r || typeof r.name !== "string") return null;
  const latitude = Number(r.latitude);
  const longitude = Number(r.longitude);
  if (!Number.isFinite(latitude) || Math.abs(latitude) > 90) return null;
  if (!Number.isFinite(longitude) || Math.abs(longitude) > 180) return null;
  if (!isValidTimezone(r.timezone)) return null;
  return {
    name: r.name,
    admin1: typeof r.admin1 === "string" ? r.admin1 : undefined,
    country: typeof r.country === "string" ? r.country : undefined,
    latitude,
    longitude,
    timezone: r.timezone,
  };
}

export async function searchCity(
  query: string,
  opts: { lang?: string; count?: number; signal?: AbortSignal; fetchImpl?: typeof fetch } = {}
): Promise<CityHit[]> {
  const q = query.trim();
  if (q.length < 2) return [];
  const f = opts.fetchImpl ?? fetch;
  const url =
    `${ENDPOINT}?name=${encodeURIComponent(q)}` +
    `&count=${opts.count ?? 5}&language=${LANG_MAP[opts.lang ?? "ko"] ?? "en"}&format=json`;
  const res = await f(url, { signal: opts.signal });
  if (!res.ok) throw new Error(`geocoding HTTP ${res.status}`);
  const data = await res.json();
  // 결과가 없으면 results 키 자체가 없음
  const rows: any[] = Array.isArray(data?.results) ? data.results : [];
  return rows.map(toHit).filter((h): h is CityHit => h !== null);
}

/** "서울, 서울특별시, 대한민국" 같은 표시용 라벨 */
export function hitLabel(h: CityHit): string {
  return [h.name, h.admin1, h.country].filter(Boolean).join(", ");
}

/** 그 날짜에 해당 타임존이 쓰는 UTC 오프셋(분). 계산할 수 없으면 null. (역사적 오프셋·서머타임 반영) */
export function tzOffsetMinutes(tz: string, date: Date): number | null {
  try {
    const parts = new Intl.DateTimeFormat("en-US", { timeZone: tz, timeZoneName: "longOffset" })
      .formatToParts(date);
    const name = parts.find((p) => p.type === "timeZoneName")?.value ?? "";
    if (name === "GMT") return 0;
    const m = /^GMT([+-])(\d{1,2})(?::(\d{2}))?$/.exec(name);
    if (!m) return null;
    return (Number(m[2]) * 60 + Number(m[3] ?? 0)) * (m[1] === "-" ? -1 : 1);
  } catch {
    return null;
  }
}

/** 화면 표시용: "UTC+09:00", "UTC+08:30", "UTC-04:00" */
export function tzOffsetLabel(tz: string, date: Date): string | null {
  const min = tzOffsetMinutes(tz, date);
  if (min === null) return null;
  const sign = min < 0 ? "-" : "+";
  const abs = Math.abs(min);
  return `UTC${sign}${String(Math.floor(abs / 60)).padStart(2, "0")}:${String(abs % 60).padStart(2, "0")}`;
}

/** 타임존의 표준 자오선 (예: +09:00 -> 135°). 경도 1° = 4분. */
export function standardMeridianLongitude(tz: string, date: Date): number | null {
  const min = tzOffsetMinutes(tz, date);
  return min === null ? null : min / 4;
}

// 타임존 선택 목록(TIMEZONE_LIST)의 대표 도시 경도. 경도를 비워뒀을 때의 기본값.
const TZ_REPRESENTATIVE: Record<string, number> = {
  "Asia/Seoul": 126.978, "Asia/Tokyo": 139.65, "Asia/Shanghai": 121.474, "Asia/Hong_Kong": 114.169,
  "Asia/Taipei": 121.565, "Asia/Singapore": 103.82, "Asia/Bangkok": 100.502, "Asia/Jakarta": 106.845,
  "Asia/Manila": 120.984, "Asia/Dubai": 55.271, "Europe/London": -0.128, "Europe/Paris": 2.352,
  "Europe/Berlin": 13.405, "Europe/Moscow": 37.618, "Europe/Madrid": -3.704, "Europe/Rome": 12.496,
  "America/New_York": -74.006, "America/Chicago": -87.63, "America/Los_Angeles": -118.244,
  "America/Sao_Paulo": -46.633, "Australia/Sydney": 151.209, "Pacific/Auckland": 174.763,
  "Africa/Cairo": 31.236, UTC: 0,
};

/** 경도를 모를 때 쓸 값: 대표 도시 경도 -> 없으면 표준 자오선(보정 0) -> 계산 불가면 null */
export function defaultLongitudeForTimezone(tz: string, date: Date): number | null {
  if (tz in TZ_REPRESENTATIVE) return TZ_REPRESENTATIVE[tz];
  return standardMeridianLongitude(tz, date);
}

/** 경도가 그 타임존과 어울리는지(표준 자오선에서 maxDiff° 이내, 날짜변경선 고려). 계산 불가면 true. */
export function isLongitudeConsistent(lon: number, tz: string, date: Date, maxDiff = 50): boolean {
  const mer = standardMeridianLongitude(tz, date);
  if (mer === null) return true;
  const d = ((((lon - mer) % 360) + 360 + 180) % 360) - 180;
  return Math.abs(d) <= maxDiff;
}

/** 입력 중 연속 호출을 모아서(debounce) 마지막 입력만 조회하고, 늦게 도착한 옛 응답은 버린다. */
export function createCityLookup(
  onState: (s: { status: "idle" | "loading" | "found" | "notfound" | "error"; hits: CityHit[] }) => void,
  opts: { lang?: string; debounceMs?: number; fetchImpl?: typeof fetch } = {}
) {
  let timer: ReturnType<typeof setTimeout> | null = null;
  let ctrl: AbortController | null = null;
  let seq = 0;

  const cancel = () => {
    if (timer) clearTimeout(timer);
    timer = null;
    ctrl?.abort();
    ctrl = null;
  };

  return {
    search(query: string) {
      cancel();
      const q = query.trim();
      if (q.length < 2) {
        onState({ status: "idle", hits: [] });
        return;
      }
      const mine = ++seq;
      timer = setTimeout(async () => {
        ctrl = new AbortController();
        onState({ status: "loading", hits: [] });
        try {
          const hits = await searchCity(q, { lang: opts.lang, signal: ctrl.signal, fetchImpl: opts.fetchImpl });
          if (mine !== seq) return; // 그 사이 새 입력이 있었음
          onState({ status: hits.length ? "found" : "notfound", hits });
        } catch (e: any) {
          if (mine !== seq || e?.name === "AbortError") return;
          onState({ status: "error", hits: [] });
        }
      }, opts.debounceMs ?? 500);
    },
    cancel,
  };
}
