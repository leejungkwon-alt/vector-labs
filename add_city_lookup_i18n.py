#!/usr/bin/env python3
"""frontend/src/locales/{ko,en,ja,zh_cn,es}.json 의 "birthInput" 안에 도시 조회 안내 문구 5개를 추가합니다.
파일 전체를 다시 쓰지 않고 해당 위치에만 끼워 넣어서 서식/줄바꿈(CRLF)이 그대로 유지됩니다. 여러 번 실행해도 안전합니다.
프로젝트 루트에서:  python add_city_lookup_i18n.py"""
import json, re, sys
from pathlib import Path

TEXT = {
 "ko":    ("도시를 찾는 중…", "도시를 찾지 못했어요. 철자를 확인하거나 경도와 타임존을 직접 입력해 주세요.", "도시 검색에 실패했어요. 경도와 타임존을 직접 입력해 주세요.", "출생일 기준 UTC 오프셋", "경도는 -180 ~ 180 사이의 숫자로 입력해 주세요."),
 "en":    ("Looking up city…", "City not found. Check the spelling or enter longitude and timezone manually.", "City search failed. Please enter longitude and timezone manually.", "UTC offset on birth date", "Enter longitude as a number between -180 and 180."),
 "ja":    ("都市を検索中…", "都市が見つかりませんでした。つづりを確認するか、経度とタイムゾーンを手動で入力してください。", "都市の検索に失敗しました。経度とタイムゾーンを手動で入力してください。", "出生日時点のUTCオフセット", "経度は-180〜180の数値で入力してください。"),
 "zh_cn": ("正在查找城市…", "未找到该城市。请检查拼写，或手动输入经度和时区。", "城市搜索失败，请手动输入经度和时区。", "出生日的UTC偏移", "请输入-180至180之间的经度数值。"),
 "es":    ("Buscando la ciudad…", "No se encontró la ciudad. Revisa la ortografía o introduce la longitud y la zona horaria manualmente.", "La búsqueda de la ciudad falló. Introduce la longitud y la zona horaria manualmente.", "Desfase UTC en la fecha de nacimiento", "Introduce la longitud como un número entre -180 y 180."),
}
KEYS = ("cityLookupLoading", "cityLookupNotFound", "cityLookupError", "tzOffsetAtBirth", "longitudeInvalid")
base = Path("frontend/src/locales")
for lang, vals in TEXT.items():
    p = base / f"{lang}.json"
    raw = p.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    data = json.loads(raw)
    bi = data.get("birthInput")
    if bi is None: print(f"[건너뜀] {p}: birthInput 없음"); continue
    missing = [(k, v) for k, v in zip(KEYS, vals) if k not in bi]
    if not missing: print(f"[이미 있음] {p}"); continue
    m = re.search(r'^([ \t]*)"birthInput"\s*:\s*\{[ \t]*\r?\n([ \t]*)"', raw, re.M)
    if not m: print(f"[건너뜀] {p}: birthInput 위치를 찾지 못함 (수동 추가 필요)"); continue
    indent = m.group(2)
    ins = "".join(f'{indent}{json.dumps(k)}: {json.dumps(v, ensure_ascii=False)},{nl}' for k, v in missing)
    pos = m.end() - len(indent) - 1          # 첫 키가 시작되는 줄의 맨 앞
    out = raw[:pos] + ins + raw[pos:]
    json.loads(out)                           # 결과가 올바른 JSON 인지 확인 후에만 저장
    p.write_bytes(out.encode("utf-8"))
    print(f"[추가] {p}: {', '.join(k for k, _ in missing)}")
