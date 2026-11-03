$ErrorActionPreference = "Stop"
$utf8NoBom = New-Object System.Text.UTF8Encoding $false

function Write-File($path, $content) {
    [System.IO.File]::WriteAllText((Resolve-Path $path), $content, $utf8NoBom)
}
function Read-File($path) {
    [System.IO.File]::ReadAllText((Resolve-Path $path), [System.Text.Encoding]::UTF8)
}

# ---------- backup ----------
Copy-Item "app\auth\router.py"            "app\auth\router.py.bak"            -Force
Copy-Item "frontend\src\api\client.ts"    "frontend\src\api\client.ts.bak"    -Force
Write-Host "[backup] .bak created" -ForegroundColor Yellow

# ---------- P0-3 ----------
Write-Host "`n=== P0-3: app\auth\router.py ===" -ForegroundColor Cyan
$p3 = "app\auth\router.py"
$c3 = Read-File $p3

# 1) ensure platform field on PurchaseRequest
$anchor = 'class PurchaseRequest(BaseModel):'
$idx = $c3.IndexOf($anchor)
if ($idx -lt 0) {
    throw "PurchaseRequest class not found in $p3"
}
$sliceEnd = [Math]::Min($c3.Length, $idx + 400)
$block = $c3.Substring($idx, $sliceEnd - $idx)
if ($block -match '(?m)^\s+platform\s*:') {
    Write-Host "  [skip] platform field already present" -ForegroundColor Gray
} else {
    $patternField = 'class PurchaseRequest\(BaseModel\):\r?\n(\s+product_id: str\r?\n\s+receipt: str = "mock_valid_receipt")'
    if ($c3 -match $patternField) {
        $c3 = $c3 -replace $patternField, ("class PurchaseRequest(BaseModel):`r`n`$1`r`n    platform: str")
        Write-Host "  [ok] added 'platform: str'" -ForegroundColor Green
    } else {
        throw "PurchaseRequest body shape unexpected; open file and inspect manually"
    }
}

# 2) stop hardcoding "ios"
if ($c3 -match 'verify_and_grant\(user\["id"\], "ios",') {
    $c3 = $c3 -replace 'verify_and_grant\(user\["id"\], "ios",', 'verify_and_grant(user["id"], body.platform,'
    Write-Host "  [ok] verify_and_grant uses body.platform" -ForegroundColor Green
} else {
    Write-Host "  [skip] call already updated" -ForegroundColor Gray
}

Write-File $p3 $c3

# ---------- P0-4 ----------
Write-Host "`n=== P0-4: frontend\src\api\client.ts ===" -ForegroundColor Cyan
$p4 = "frontend\src\api\client.ts"
$c4 = Read-File $p4

$pat4 = '(?m)^([ \t]*)if \(typeof console !== "undefined"\) console\.warn\("\[client\] EXPO_PUBLIC_API_BASE_URL not set"\);\r?\n[ \t]*return "";\s*$'
if ($c4 -match $pat4) {
    $indent = $Matches[1]
    $rep = ($indent + 'throw new Error(' + "`r`n" +
            $indent + '  "[client] EXPO_PUBLIC_API_BASE_URL is not set. Set it in the build environment before bundling.",' + "`r`n" +
            $indent + ');')
    $c4 = $c4 -replace $pat4, $rep
    Write-Host "  [ok] silent return replaced with fail-fast throw" -ForegroundColor Green
    Write-File $p4 $c4
} else {
    Write-Host "  [skip] already updated or pattern not found" -ForegroundColor Gray
}

# ---------- verify ----------
Write-Host "`n=== VERIFY ===" -ForegroundColor Cyan
Write-Host "--- router.py ---"
Select-String -Path $p3 -Pattern 'class PurchaseRequest|platform|verify_and_grant\(' -Context 0,1 | ForEach-Object { $_.Line }
Write-Host "--- client.ts ---"
Select-String -Path $p4 -Pattern 'EXPO_PUBLIC_API_BASE_URL|throw new Error|return ""' | ForEach-Object { $_.Line }

Write-Host "`n[rollback] Copy-Item app\auth\router.py.bak app\auth\router.py -Force" -ForegroundColor Yellow
Write-Host "[rollback] Copy-Item frontend\src\api\client.ts.bak frontend\src\api\client.ts -Force" -ForegroundColor Yellow