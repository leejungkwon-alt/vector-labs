# apply_refresh_fix.ps1
# Run from the repo root (C:\SAJU):
#   powershell -ExecutionPolicy Bypass -File .\apply_refresh_fix.ps1
# After a successful Google Play purchase, refetch all react-query data
# (including the report on the home tab) so locked content opens immediately.
# Safe to run twice. Original is backed up to .\_backup_google_billing\.
# (ASCII only on purpose: Windows PowerShell 5.1 misreads UTF-8 without BOM.)

$ErrorActionPreference = "Stop"
$Root = (Get-Location).Path
$utf8 = New-Object System.Text.UTF8Encoding($false)
$modal = Join-Path $Root "frontend\src\components\PaymentModal.tsx"
$pkg   = Join-Path $Root "frontend\package.json"
$BackupDir = Join-Path $Root "_backup_google_billing"

if (-not (Test-Path $modal)) { throw "Not found: $modal (run this from C:\SAJU)" }
if (-not (Test-Path $pkg))   { throw "Not found: $pkg" }

$pk = [System.IO.File]::ReadAllText($pkg, [System.Text.Encoding]::UTF8)
if     ($pk.Contains('"@tanstack/react-query"')) { $lib = "@tanstack/react-query" }
elseif ($pk.Contains('"react-query"'))           { $lib = "react-query" }
else { throw "react-query not found in frontend\package.json - tell Claude which data library the app uses" }

$t = [System.IO.File]::ReadAllText($modal, [System.Text.Encoding]::UTF8)
if ($t.Contains("useQueryClient")) { Write-Host "PaymentModal.tsx already patched"; exit 0 }
$nl = if ($t.Contains("`r`n")) { "`r`n" } else { "`n" }

function Add-After([string]$text, [string]$anchorPattern, [string]$addition) {
    if ($text -notmatch $anchorPattern) { throw "Anchor not found: $anchorPattern" }
    return [regex]::Replace($text, $anchorPattern, { param($m) $m.Value + $nl + $addition }, 1)
}

# 1) import
$t = Add-After $t 'import \{ useAuthStore \} from "@/store/authStore";' ('import { useQueryClient } from "' + $lib + '";')
# 2) hook
$t = Add-After $t 'const bootstrap = useAuthStore\(\(s\) => s\.bootstrap\);' '  const queryClient = useQueryClient();'
# 3) ref
$t = Add-After $t 'const bootstrapRef = useRef\(bootstrap\);' '  const queryClientRef = useRef(queryClient);'
# 4) keep ref fresh
$t = Add-After $t 'useEffect\(\(\) => \{ bootstrapRef\.current = bootstrap; \}, \[bootstrap\]\);' '  useEffect(() => { queryClientRef.current = queryClient; }, [queryClient]);'
# 5) refetch after success (inside the purchase listener)
$t = Add-After $t 'bootstrapRef\.current\(\);' '          queryClientRef.current.invalidateQueries(); // refetch report/daily/etc. so locked content opens'

if (-not (Test-Path $BackupDir)) { New-Item -ItemType Directory -Path $BackupDir | Out-Null }
Copy-Item $modal (Join-Path $BackupDir "PaymentModal.tsx.before_refresh_fix") -Force
[System.IO.File]::WriteAllText($modal, $t, $utf8)
Write-Host "PaymentModal.tsx patched (library: $lib)"
git --no-pager diff --stat -- $modal