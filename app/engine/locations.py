# app/engine/locations.py
"""
City presets — 위경도 + IANA timezone + region bucket.

총 53개 도시. 사용자는 `birth_location` 키 하나로 정확한 LMT + tz를 얻는다.
직접 좌표를 지정하려면 `birth_location` 없이 `longitude`/`timezone_str`을 넘기면 된다.

`region` 버킷은 이후 콘텐츠 tone 조정에만 사용 (Step 9-B).
"""

CITY_PRESETS = {
    # ---- Korea (13) ----
    "seoul":        {"name": "서울", "lat": 37.5665, "lon": 126.9780, "tz": "Asia/Seoul",       "region": "KOREA"},
    "busan":        {"name": "부산", "lat": 35.1796, "lon": 129.0756, "tz": "Asia/Seoul",       "region": "KOREA"},
    "incheon":      {"name": "인천", "lat": 37.4563, "lon": 126.7052, "tz": "Asia/Seoul",       "region": "KOREA"},
    "daegu":        {"name": "대구", "lat": 35.8714, "lon": 128.6014, "tz": "Asia/Seoul",       "region": "KOREA"},
    "daejeon":      {"name": "대전", "lat": 36.3504, "lon": 127.3845, "tz": "Asia/Seoul",       "region": "KOREA"},
    "gwangju":      {"name": "광주", "lat": 35.1595, "lon": 126.8526, "tz": "Asia/Seoul",       "region": "KOREA"},
    "ulsan":        {"name": "울산", "lat": 35.5384, "lon": 129.3114, "tz": "Asia/Seoul",       "region": "KOREA"},
    "suwon":        {"name": "수원", "lat": 37.2636, "lon": 127.0286, "tz": "Asia/Seoul",       "region": "KOREA"},
    "changwon":     {"name": "창원", "lat": 35.2280, "lon": 128.6811, "tz": "Asia/Seoul",       "region": "KOREA"},
    "goyang":       {"name": "고양", "lat": 37.6584, "lon": 126.8320, "tz": "Asia/Seoul",       "region": "KOREA"},
    "yongin":       {"name": "용인", "lat": 37.2411, "lon": 127.1776, "tz": "Asia/Seoul",       "region": "KOREA"},
    "seongnam":     {"name": "성남", "lat": 37.4200, "lon": 127.1265, "tz": "Asia/Seoul",       "region": "KOREA"},
    "jeonju":       {"name": "전주", "lat": 35.8242, "lon": 127.1480, "tz": "Asia/Seoul",       "region": "KOREA"},

    # ---- Japan (5) ----
    "tokyo":        {"name": "도쿄",   "lat": 35.6762, "lon": 139.6503, "tz": "Asia/Tokyo",  "region": "JAPAN"},
    "osaka":        {"name": "오사카", "lat": 34.6937, "lon": 135.5023, "tz": "Asia/Tokyo",  "region": "JAPAN"},
    "nagoya":       {"name": "나고야", "lat": 35.1815, "lon": 136.9066, "tz": "Asia/Tokyo",  "region": "JAPAN"},
    "sapporo":      {"name": "삿포로", "lat": 43.0618, "lon": 141.3545, "tz": "Asia/Tokyo",  "region": "JAPAN"},
    "fukuoka":      {"name": "후쿠오카","lat": 33.5904, "lon": 130.4017, "tz": "Asia/Tokyo", "region": "JAPAN"},

    # ---- Greater China / HK / TW / SG (5) ----
    "beijing":      {"name": "베이징",      "lat": 39.9042, "lon": 116.4074, "tz": "Asia/Shanghai",  "region": "GREATER_CHINA"},
    "shanghai":     {"name": "상하이",      "lat": 31.2304, "lon": 121.4737, "tz": "Asia/Shanghai",  "region": "GREATER_CHINA"},
    "hong_kong":    {"name": "홍콩",        "lat": 22.3193, "lon": 114.1694, "tz": "Asia/Hong_Kong", "region": "GREATER_CHINA"},
    "taipei":       {"name": "타이베이",    "lat": 25.0330, "lon": 121.5654, "tz": "Asia/Taipei",    "region": "GREATER_CHINA"},
    "singapore":    {"name": "싱가포르",    "lat":  1.3521, "lon": 103.8198, "tz": "Asia/Singapore", "region": "SOUTHEAST_ASIA"},

    # ---- US (8) ----
    "new_york":     {"name": "뉴욕",       "lat": 40.7128, "lon": -74.0060,  "tz": "America/New_York",    "region": "NORTH_AMERICA"},
    "los_angeles":  {"name": "로스앤젤레스","lat": 34.0522, "lon": -118.2437, "tz": "America/Los_Angeles", "region": "NORTH_AMERICA"},
    "chicago":      {"name": "시카고",     "lat": 41.8781, "lon": -87.6298,  "tz": "America/Chicago",     "region": "NORTH_AMERICA"},
    "houston":      {"name": "휴스턴",     "lat": 29.7604, "lon": -95.3698,  "tz": "America/Chicago",     "region": "NORTH_AMERICA"},
    "phoenix":      {"name": "피닉스",     "lat": 33.4484, "lon": -112.0740, "tz": "America/Phoenix",     "region": "NORTH_AMERICA"},
    "philadelphia": {"name": "필라델피아", "lat": 39.9526, "lon": -75.1652,  "tz": "America/New_York",    "region": "NORTH_AMERICA"},
    "san_francisco":{"name": "샌프란시스코","lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles", "region": "NORTH_AMERICA"},
    "seattle":      {"name": "시애틀",     "lat": 47.6062, "lon": -122.3321, "tz": "America/Los_Angeles", "region": "NORTH_AMERICA"},

    # ---- Canada (2) ----
    "toronto":      {"name": "토론토",   "lat": 43.6532, "lon": -79.3832,  "tz": "America/Toronto",   "region": "NORTH_AMERICA"},
    "vancouver":    {"name": "밴쿠버",   "lat": 49.2827, "lon": -123.1207, "tz": "America/Vancouver", "region": "NORTH_AMERICA"},

    # ---- Europe (10) ----
    "london":       {"name": "런던",     "lat": 51.5074, "lon": -0.1278, "tz": "Europe/London",    "region": "EUROPE"},
    "paris":        {"name": "파리",     "lat": 48.8566, "lon":  2.3522, "tz": "Europe/Paris",     "region": "EUROPE"},
    "berlin":       {"name": "베를린",   "lat": 52.5200, "lon": 13.4050, "tz": "Europe/Berlin",    "region": "EUROPE"},
    "madrid":       {"name": "마드리드", "lat": 40.4168, "lon": -3.7038, "tz": "Europe/Madrid",    "region": "EUROPE"},
    "rome":         {"name": "로마",     "lat": 41.9028, "lon": 12.4964, "tz": "Europe/Rome",      "region": "EUROPE"},
    "amsterdam":    {"name": "암스테르담","lat": 52.3676, "lon":  4.9041, "tz": "Europe/Amsterdam", "region": "EUROPE"},
    "stockholm":    {"name": "스톡홀름", "lat": 59.3293, "lon": 18.0686, "tz": "Europe/Stockholm", "region": "EUROPE"},
    "zurich":       {"name": "취리히",   "lat": 47.3769, "lon":  8.5417, "tz": "Europe/Zurich",    "region": "EUROPE"},
    "dublin":       {"name": "더블린",   "lat": 53.3498, "lon": -6.2603, "tz": "Europe/Dublin",    "region": "EUROPE"},
    "barcelona":    {"name": "바르셀로나","lat": 41.3851, "lon":  2.1734, "tz": "Europe/Madrid",   "region": "EUROPE"},

    # ---- Southeast Asia (4) ----
    "bangkok":      {"name": "방콕",         "lat": 13.7563, "lon": 100.5018, "tz": "Asia/Bangkok",      "region": "SOUTHEAST_ASIA"},
    "jakarta":      {"name": "자카르타",     "lat": -6.2088, "lon": 106.8456, "tz": "Asia/Jakarta",      "region": "SOUTHEAST_ASIA"},
    "manila":       {"name": "마닐라",       "lat": 14.5995, "lon": 120.9842, "tz": "Asia/Manila",       "region": "SOUTHEAST_ASIA"},
    "kuala_lumpur": {"name": "쿠알라룸푸르", "lat":  3.1390, "lon": 101.6869, "tz": "Asia/Kuala_Lumpur", "region": "SOUTHEAST_ASIA"},

    # ---- Middle East (2) ----
    "dubai":        {"name": "두바이",   "lat": 25.2048, "lon": 55.2708, "tz": "Asia/Dubai",     "region": "MIDDLE_EAST"},
    "tel_aviv":     {"name": "텔아비브", "lat": 32.0853, "lon": 34.7818, "tz": "Asia/Jerusalem", "region": "MIDDLE_EAST"},

    # ---- LATAM (2) ----
    "sao_paulo":    {"name": "상파울루",  "lat": -23.5505, "lon": -46.6333, "tz": "America/Sao_Paulo",  "region": "LATAM"},
    "mexico_city":  {"name": "멕시코시티","lat": 19.4326,  "lon": -99.1332, "tz": "America/Mexico_City","region": "LATAM"},

    # ---- Oceania (2) ----
    "sydney":       {"name": "시드니",   "lat": -33.8688, "lon": 151.2093, "tz": "Australia/Sydney",   "region": "OCEANIA"},
    "melbourne":    {"name": "멜버른",   "lat": -37.8136, "lon": 144.9631, "tz": "Australia/Melbourne","region": "OCEANIA"},
}


def resolve_location(city_key: str) -> tuple[float, str, str]:
    """
    도시 키 → (lon, tz, region).

    Raises:
        ValueError: 알 수 없는 도시 키
    """
    key = city_key.lower().strip()
    preset = CITY_PRESETS.get(key)
    if preset is None:
        sample = sorted(CITY_PRESETS.keys())[:10]
        raise ValueError(
            f"Unknown city key: {city_key!r}. "
            f"Known cities start with: {sample}... "
            f"Pass `longitude` + `timezone_str` instead if you need a custom location."
        )
    return preset["lon"], preset["tz"], preset["region"]


def list_cities(region: str | None = None) -> list[dict]:
    """도시 목록. region 필터 가능."""
    items = []
    for key, preset in CITY_PRESETS.items():
        if region and preset["region"] != region:
            continue
        items.append({"key": key, **preset})
    return sorted(items, key=lambda x: x["key"])