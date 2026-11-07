# scripts/validate_famous.py
"""
유명인 사주 결과를 백엔드 API로 조회해서 파일로 저장.
실제 인생사와 비교 검증용.
"""
import json
import sys
import time
import httpx
from pathlib import Path

API_BASE = "https://saju-backend-787049663118.asia-northeast3.run.app/api/v1"
OUT_DIR = Path("scripts/famous_reports")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 출생 시간이 공개적으로 신뢰도 있게 알려진 인물 위주
PEOPLE = [
    {
        "name": "Steve Jobs",
        "birth_date": "1955-02-24",
        "birth_time": "19:15:00",
        "timezone_str": "America/Los_Angeles",
        "longitude": -122.4194,
        "gender": "M",
        "birth_location": "san_francisco",
        "known_for": "Apple 창업, 혁신적 리더십, 56세 사망(췌장암)",
    },
    {
        "name": "Albert Einstein",
        "birth_date": "1879-03-14",
        "birth_time": "11:30:00",
        "timezone_str": "Europe/Berlin",
        "longitude": 9.9937,
        "gender": "M",
        "birth_location": "ulm",
        "known_for": "상대성이론, 노벨물리학상, 천재적 사유, 만년 고립",
    },
    {
        "name": "Barack Obama",
        "birth_date": "1961-08-04",
        "birth_time": "19:24:00",
        "timezone_str": "Pacific/Honolulu",
        "longitude": -157.8583,
        "gender": "M",
        "birth_location": "honolulu",
        "known_for": "미국 첫 흑인 대통령, 카리스마, 설득력",
    },
    {
        "name": "Princess Diana",
        "birth_date": "1961-07-01",
        "birth_time": "19:45:00",
        "timezone_str": "Europe/London",
        "longitude": -0.5000,
        "gender": "F",
        "birth_location": "sandringham",
        "known_for": "자선활동, 대중적 사랑, 파란만장한 결혼생활, 36세 요절",
    },
    {
        "name": "Marilyn Monroe",
        "birth_date": "1926-06-01",
        "birth_time": "09:30:00",
        "timezone_str": "America/Los_Angeles",
        "longitude": -118.2437,
        "gender": "F",
        "birth_location": "los_angeles",
        "known_for": "할리우드 아이콘, 매력적 매혹, 불안정한 내면, 36세 사망",
    },
    {
        "name": "IU (이지은)",
        "birth_date": "1993-05-16",
        "birth_time": "12:00:00",  # 시간 미확인, 정오 가정
        "timezone_str": "Asia/Seoul",
        "longitude": 126.978,
        "gender": "F",
        "birth_location": "seoul",
        "known_for": "싱어송라이터, 배우, 자선활동, 안정적 성장",
    },
]


def main():
    # 1. 익명 토큰 발급
    print("=" * 55)
    print("익명 토큰 발급 중...")
    print("=" * 55)
    with httpx.Client(timeout=30) as c:
        r = c.post(f"{API_BASE}/auth/anonymous")
        r.raise_for_status()
        token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. 각 인물별 사주 계산
    for p in PEOPLE:
        print(f"\n{'='*55}")
        print(f"🔮 {p['name']}  ({p['birth_date']} {p['birth_time'][:5]})")
        print(f"   → {p['known_for']}")
        print("=" * 55)

        payload = {
            "birth_date": p["birth_date"],
            "birth_time": p["birth_time"],
            "birth_time_mode": "exact",
            "timezone_str": p["timezone_str"],
            "longitude": p["longitude"],
            "correction_mode": "lmt",
            "jasi_boundary": 23,
            "gender": p["gender"],
            "birth_location": p.get("birth_location"),
            "lang": "ko",
        }

        try:
            with httpx.Client(timeout=60) as c:
                r = c.post(f"{API_BASE}/saju/calculate",
                           json=payload, headers=headers)
                r.raise_for_status()
                result = r.json()
        except Exception as e:
            print(f"  ❌ 실패: {e}")
            continue

        # 결과 요약 출력
        arch = result.get("archetype", {})
        energy = result.get("energy_signature", {})
        pillars = result.get("pillars", {})

        print(f"  사주(四柱): 년={pillars.get('year_pillar','?')} "
              f"월={pillars.get('month_pillar','?')} "
              f"일={pillars.get('day_pillar','?')} "
              f"시={pillars.get('hour_pillar','?')}")
        print(f"  아키타입: {arch.get('name_ko', '?')} ({arch.get('stem','?')})")
        print(f"  오행비율: {energy.get('percentages', {})}")

        # 파일 저장
        out_path = OUT_DIR / f"{p['name'].replace(' ', '_')}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump({
                "person": p,
                "saju_result": result,
            }, f, ensure_ascii=False, indent=2)
        print(f"  💾 저장: {out_path}")

        time.sleep(2)  # rate limit 여유

    print(f"\n🎉 완료. {OUT_DIR}/ 폴더에서 결과 확인.")


if __name__ == "__main__":
    main()