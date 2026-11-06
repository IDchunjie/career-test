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

$working = $null
foreach ($ip in $ips) {
    $code = & curl.exe -s -o NUL -w "%{http_code}" --max-time 6 --resolve "github.com:443:$ip" https://github.com 2>$null
    if (-not $code) { $code = "000" }
    Write-Host ("  测试 {0,-18} -> {1}" -f $ip, $code)
    if ($code -eq "200") { $working = $ip; break }
}

if (-not $working) {
    Write-Host ""
    Write-Host "当前没有可用的 GitHub IP。" -ForegroundColor Yellow
    Write-Host "可以稍后再试，或者用手机开热点再运行本脚本。"
    exit 1
}

Copy-Item $hosts "$hosts.bak" -Force

$lines = Get-Content $hosts -ErrorAction SilentlyContinue |
    Where-Object { $_ -notmatch "github\.com" }
$lines = @($lines) + @("", "$working github.com")

Set-Content -Path $hosts -Value $lines -Encoding ASCII
ipconfig /flushdns | Out-Null

Write-Host ""
Write-Host ("已写入: {0} github.com" -f $working) -ForegroundColor Green

Start-Sleep -Seconds 1
$test = & curl.exe -s -o NUL -w "%{http_code}" --max-time 10 https://github.com 2>$null
Write-Host ("验证访问 github.com -> {0}" -f $test)
