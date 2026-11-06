$ErrorActionPreference = "Continue"
$hosts = "$env:SystemRoot\System32\drivers\etc\hosts"

$ips = @(
    "140.82.112.3", "140.82.112.4",
    "140.82.113.3", "140.82.113.4",
    "140.82.114.3", "140.82.114.4",
    "140.82.116.3", "140.82.116.4",
    "140.82.121.3", "140.82.121.4",
    "20.205.243.166", "20.27.177.113",
    "20.200.245.247", "20.233.83.145"
)

function Test-GitHubIp($ip) {
    $code = & curl.exe -s -o NUL -w "%{http_code}" --max-time 6 --resolve "github.com:443:$ip" https://github.com 2>$null
    if (-not $code) { return "000" }
    return [string]$code
}

$working = $null
foreach ($ip in $ips) {
    $code = Test-GitHubIp $ip
    Write-Host ("  try {0,-18} -> {1}" -f $ip, $code)
    if ($code -eq "200") { $working = $ip; break }
}

if (-not $working) {
    Write-Host ""
    Write-Host "No working GitHub IP right now." -ForegroundColor Yellow
    Write-Host "Try again later, or switch to a phone hotspot."
    exit 1
}

# 读 hosts（用 .NET，免得管道遇到编码/锁问题）
$text = ""
for ($i = 1; $i -le 3; $i++) {
    try { $text = [System.IO.File]::ReadAllText($hosts); break }
    catch { Start-Sleep -Seconds 1 }
}

$kept = @()
foreach ($line in ($text -split "`r?`n")) {
    if ($line -match "github\.com") { continue }
    $kept += $line
}
$newText = ($kept -join "`r`n").TrimEnd() + "`r`n" + "$working github.com`r`n"

$ok = $false
for ($i = 1; $i -le 3; $i++) {
    try {
        [System.IO.File]::WriteAllText($hosts, $newText, [System.Text.Encoding]::ASCII)
        $ok = $true
        break
    } catch {
        Write-Host "  hosts busy, retry $i ..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
}

if ($ok) {
    ipconfig /flushdns | Out-Null
    Write-Host ""
    Write-Host ("OK: {0} github.com" -f $working) -ForegroundColor Green
} else {
    Write-Host "Could not write hosts (file busy). Not fatal if github.com already works." -ForegroundColor Yellow
}

Start-Sleep -Seconds 1
$test = & curl.exe -s -o NUL -w "%{http_code}" --max-time 10 https://github.com 2>$null
Write-Host ("check github.com -> {0}" -f $test)
