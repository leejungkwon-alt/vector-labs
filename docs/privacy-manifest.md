# Apple Privacy Manifest 요약

> App Store 제출 시 `PrivacyInfo.xcprivacy` 파일에 매핑할 항목 정리.

## NSPrivacyTracking
- `false` — 추적(tracking) 없음

## NSPrivacyCollectedDataTypes
| 데이터 유형 | Linked to user | Tracking | 목적 |
|---|---|---|---|
| `NSPrivacyCollectedDataTypeDateOfBirth` | yes | no | App Functionality |
| `NSPrivacyCollectedDataTypeSensitiveInfo` | yes | no | App Functionality |
| `NSPrivacyCollectedDataTypeCoarseLocation` | yes | no | App Functionality |
| `NSPrivacyCollectedDataTypeUserID` | yes | no | App Functionality |

## NSPrivacyAccessedAPITypes
| API 카테고리 | 이유 |
|---|---|
| `NSPrivacyAccessedAPICategoryUserDefaults` | `CA92.1` |
| `NSPrivacyAccessedAPICategoryFileTimestamp` | `C617.1` |

## 참고
- 실제 매니페스트는 `app.json`의 `expo.ios.privacyManifests` 필드에도 반영되어 있습니다.
