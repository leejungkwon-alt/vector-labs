# Security Audit Notes

## 2026-10-25 — P1-1 OIDC 스모크 시점

`npm audit --omit=dev` 결과: 9 vulns (3 moderate, 6 high).

원인: 전부 `expo`의 transitive build-time toolchain.
- `node-forge` (high) — `@expo/cli` → `@expo/code-signing-certificates`
- `zod` (high) — `@expo/cli`
- `uuid` (moderate) — `@expo/config-plugins` → `xcode`

**결정: 수용 (accept).**
- 런타임 노출 없음: Metro 번들·앱 바이너리에 포함되지 않는 dev/CI 도구만 해당.
- `npm audit fix --force` 금지: `expo@58.0.16 → 44.0.6` 다운그레이드 유발.
- 대응: Expo SDK 59+ 메이저 bump 시 재확인. 그때까지 이 스냅샷 유지.