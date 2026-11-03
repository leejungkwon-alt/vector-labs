$ErrorActionPreference = "Stop"
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
$p = "frontend\src\api\client.ts"

Copy-Item $p "$p.bak" -Force
$c = [System.IO.File]::ReadAllText((Resolve-Path $p), [System.Text.Encoding]::UTF8)

# 1) Platform import 추가 (없을 때만)
if ($c -notmatch 'import\s*\{[^}]*\bPlatform\b[^}]*\}\s*from\s*"react-native"') {
    if ($c -match '(from "\.\./\.\./types";\r?\n)') {
        $c = $c -replace '(from "\.\./\.\./types";\r?\n)', "`$1import { Platform } from `"react-native`";`r`n"
        Write-Host "[ok] added react-native Platform import" -ForegroundColor Green
    } else {
        throw "anchor 'from ""../../types"";' not found"
    }
} else {
    Write-Host "[skip] Platform import already present" -ForegroundColor Gray
}

# 2) purchase body에 platform 추가
$pat = 'body:\s*JSON\.stringify\(\{\s*product_id,\s*receipt:\s*"mock_valid_receipt"\s*\}\)'
if ($c -match $pat) {
    $c = $c -replace $pat, 'body: JSON.stringify({ product_id, receipt: "mock_valid_receipt", platform: Platform.OS })'
    Write-Host "[ok] purchase() sends platform: Platform.OS" -ForegroundColor Green
} else {
    Write-Host "[skip] purchase body already updated or pattern mismatch" -ForegroundColor Gray
}

[System.IO.File]::WriteAllText((Resolve-Path $p), $c, $utf8NoBom)

Write-Host "`n=== VERIFY ===" -ForegroundColor Cyan
Select-String -Path $p -Pattern 'react-native|purchase:|platform' | ForEach-Object { $_.Line }