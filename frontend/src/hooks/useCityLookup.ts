// frontend/src/hooks/useCityLookup.ts
import { useEffect, useMemo, useState } from "react";
import { createCityLookup, CityHit } from "../utils/cityLookup";

type State = { status: "idle" | "loading" | "found" | "notfound" | "error"; hits: CityHit[] };

/** 도시 이름 입력 -> (0.5초 멈추면) 후보 조회. status/hits 와 search(query) 를 돌려줍니다. */
export function useCityLookup(lang: string, debounceMs = 500) {
  const [state, setState] = useState<State>({ status: "idle", hits: [] });
  const lookup = useMemo(() => createCityLookup(setState, { lang, debounceMs }), [lang, debounceMs]);
  useEffect(() => () => lookup.cancel(), [lookup]);
  return { ...state, search: lookup.search, reset: () => { lookup.cancel(); setState({ status: "idle", hits: [] }); } };
}
