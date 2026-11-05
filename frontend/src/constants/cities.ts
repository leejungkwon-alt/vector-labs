export interface City {
  key: string;
  label: string;
  label_en: string;
  longitude: number;
  timezone: string;
}

export const CITY_LIST: City[] = [
  // Korea (모두 Asia/Seoul 타임존, 경도만 지역별로 다름)
  { key: "seoul", label: "서울 (Seoul)", label_en: "Seoul", longitude: 126.978, timezone: "Asia/Seoul" },
  { key: "busan", label: "부산 (Busan)", label_en: "Busan", longitude: 129.075, timezone: "Asia/Seoul" },
  { key: "incheon", label: "인천 (Incheon)", label_en: "Incheon", longitude: 126.705, timezone: "Asia/Seoul" },
  { key: "daegu", label: "대구 (Daegu)", label_en: "Daegu", longitude: 128.601, timezone: "Asia/Seoul" },
  { key: "daejeon", label: "대전 (Daejeon)", label_en: "Daejeon", longitude: 127.384, timezone: "Asia/Seoul" },
  { key: "gwangju", label: "광주 (Gwangju)", label_en: "Gwangju", longitude: 126.852, timezone: "Asia/Seoul" },
  { key: "ulsan", label: "울산 (Ulsan)", label_en: "Ulsan", longitude: 129.311, timezone: "Asia/Seoul" },
  { key: "suwon", label: "수원 (Suwon)", label_en: "Suwon", longitude: 127.028, timezone: "Asia/Seoul" },
  
  // Japan
  { key: "tokyo", label: "도쿄 (Tokyo)", label_en: "Tokyo", longitude: 139.691, timezone: "Asia/Tokyo" },
  { key: "osaka", label: "오사카 (Osaka)", label_en: "Osaka", longitude: 135.502, timezone: "Asia/Tokyo" },
  { key: "nagoya", label: "나고야 (Nagoya)", label_en: "Nagoya", longitude: 136.906, timezone: "Asia/Tokyo" },
  { key: "fukuoka", label: "후쿠오카 (Fukuoka)", label_en: "Fukuoka", longitude: 130.401, timezone: "Asia/Tokyo" },
  { key: "sapporo", label: "삿포로 (Sapporo)", label_en: "Sapporo", longitude: 141.354, timezone: "Asia/Tokyo" },
  
  // Greater China / Asia
  { key: "beijing", label: "베이징 (Beijing)", label_en: "Beijing", longitude: 116.407, timezone: "Asia/Shanghai" },
  { key: "shanghai", label: "상하이 (Shanghai)", label_en: "Shanghai", longitude: 121.473, timezone: "Asia/Shanghai" },
  { key: "hong_kong", label: "홍콩 (Hong Kong)", label_en: "Hong Kong", longitude: 114.169, timezone: "Asia/Hong_Kong" },
  { key: "taipei", label: "타이베이 (Taipei)", label_en: "Taipei", longitude: 121.565, timezone: "Asia/Taipei" },
  { key: "singapore", label: "싱가포르 (Singapore)", label_en: "Singapore", longitude: 103.819, timezone: "Asia/Singapore" },
  { key: "bangkok", label: "방콕 (Bangkok)", label_en: "Bangkok", longitude: 100.501, timezone: "Asia/Bangkok" },
  { key: "manila", label: "마닐라 (Manila)", label_en: "Manila", longitude: 120.984, timezone: "Asia/Manila" },
  
  // North America
  { key: "new_york", label: "뉴욕 (New York)", label_en: "New York", longitude: -74.006, timezone: "America/New_York" },
  { key: "los_angeles", label: "로스앤젤레스 (LA)", label_en: "LA", longitude: -118.243, timezone: "America/Los_Angeles" },
  { key: "chicago", label: "시카고 (Chicago)", label_en: "Chicago", longitude: -87.629, timezone: "America/Chicago" },
  { key: "houston", label: "휴스턴 (Houston)", label_en: "Houston", longitude: -95.369, timezone: "America/Chicago" },
  { key: "san_francisco", label: "샌프란시스코 (San Francisco)", label_en: "San Francisco", longitude: -122.419, timezone: "America/Los_Angeles" },
  { key: "seattle", label: "시애틀 (Seattle)", label_en: "Seattle", longitude: -122.332, timezone: "America/Los_Angeles" },
  { key: "toronto", label: "토론토 (Toronto)", label_en: "Toronto", longitude: -79.383, timezone: "America/Toronto" },
  { key: "vancouver", label: "밴쿠버 (Vancouver)", label_en: "Vancouver", longitude: -123.120, timezone: "America/Vancouver" },
  
  // Europe
  { key: "london", label: "런던 (London)", label_en: "London", longitude: -0.127, timezone: "Europe/London" },
  { key: "paris", label: "파리 (Paris)", label_en: "Paris", longitude: 2.352, timezone: "Europe/Paris" },
  { key: "berlin", label: "베를린 (Berlin)", label_en: "Berlin", longitude: 13.405, timezone: "Europe/Berlin" },
  { key: "madrid", label: "마드리드 (Madrid)", label_en: "Madrid", longitude: -3.703, timezone: "Europe/Madrid" },
  { key: "rome", label: "로마 (Rome)", label_en: "Rome", longitude: 12.496, timezone: "Europe/Rome" },
  { key: "amsterdam", label: "암스테르담 (Amsterdam)", label_en: "Amsterdam", longitude: 4.904, timezone: "Europe/Amsterdam" },
  { key: "zurich", label: "취리히 (Zurich)", label_en: "Zurich", longitude: 8.541, timezone: "Europe/Zurich" },
  
  // Oceania / LATAM / Middle East
  { key: "sydney", label: "시드니 (Sydney)", label_en: "Sydney", longitude: 151.209, timezone: "Australia/Sydney" },
  { key: "melbourne", label: "멜버른 (Melbourne)", label_en: "Melbourne", longitude: 144.963, timezone: "Australia/Melbourne" },
  { key: "dubai", label: "두바이 (Dubai)", label_en: "Dubai", longitude: 55.270, timezone: "Asia/Dubai" },
  { key: "sao_paulo", label: "상파울루 (Sao Paulo)", label_en: "Sao Paulo", longitude: -46.633, timezone: "America/Sao_Paulo" },
  { key: "mexico_city", label: "멕시코시티 (Mexico City)", label_en: "Mexico City", longitude: -99.133, timezone: "America/Mexico_City" },
];