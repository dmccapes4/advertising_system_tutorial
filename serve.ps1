# ============================================================================
#  Tutorial server  --  no Python, no installs. Pure Windows (.NET HttpListener).
#  Double-click serve.bat to run this. It will:
#    1. ask Windows for permission (needed to share on your network),
#    2. show your address (and a "share on Wi-Fi" link),
#    3. open the tutorial in your browser.
#  Close this window to stop the server.
# ============================================================================
param([int]$Port = 8000, [switch]$Log)

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot

# --- Make sure we're running with permission to open a network port ---------
$principal = New-Object Security.Principal.WindowsPrincipal(
    [Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Asking Windows for permission to share on your network..." -ForegroundColor Yellow
    try {
        $reArgs = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$PSCommandPath,'-Port',"$Port")
        if ($Log) { $reArgs += '-Log' }   # carry the live-log flag through elevation
        Start-Process powershell -Verb RunAs -ArgumentList $reArgs
    } catch {
        Write-Host "Permission was declined. You can still read the tutorial:" -ForegroundColor Red
        Write-Host "just double-click  index.html  instead." -ForegroundColor Red
        Read-Host "Press Enter to close"
    }
    exit
}

Set-Location $root

# --- Allow the port through the firewall (one-time, idempotent) -------------
$ruleName = "Tutorial $Port"
try {
    if (-not (Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue)) {
        New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -LocalPort $Port `
            -Protocol TCP -Action Allow -Profile Any -ErrorAction Stop | Out-Null
    }
} catch {
    try { & netsh advfirewall firewall add rule name="$ruleName" dir=in action=allow protocol=TCP localport=$Port | Out-Null } catch {}
}

# --- Find this computer's Wi-Fi / Ethernet address --------------------------
$ip = (Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object { $_.InterfaceAlias -match 'Wi-Fi|Ethernet|Wireless' -and
                   $_.IPAddress -notlike '169.*' -and $_.IPAddress -ne '127.0.0.1' } |
    Select-Object -First 1 -ExpandProperty IPAddress)

# --- Start the web server ---------------------------------------------------
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://+:$Port/")
try {
    $listener.Start()
} catch {
    Write-Host ""
    Write-Host "  Could not start the server on port $Port." -ForegroundColor Red
    Write-Host "  ($($_.Exception.Message))"
    Write-Host "  No problem - just double-click  index.html  to read the tutorial."
    Read-Host "  Press Enter to close"
    exit 1
}

try { $Host.UI.RawUI.WindowTitle = "Tutorial server (close to stop)" } catch {}
Clear-Host
Write-Host ""
Write-Host "  ===============================================================" -ForegroundColor DarkCyan
Write-Host "    Your tutorial is now running as a little web server." -ForegroundColor White
Write-Host "  ===============================================================" -ForegroundColor DarkCyan
Write-Host ""
Write-Host "    On THIS computer :  " -NoNewline; Write-Host "http://localhost:$Port" -ForegroundColor Green
if ($ip) {
    Write-Host "    Share on Wi-Fi   :  " -NoNewline; Write-Host "http://${ip}:$Port" -ForegroundColor Cyan
    Write-Host "                        ^ type that into a phone/tablet/PC on the SAME Wi-Fi"
}
Write-Host ""
Write-Host "    A browser window should open in a second. Keep THIS window open"
Write-Host "    while you (or others) are reading. Close it to stop the server."
Write-Host ""
if ($Log) {
    Write-Host "    Live request log: ON  -  every page someone opens prints below." -ForegroundColor Magenta
    Write-Host "    (time   client-IP        method  path  -> status)" -ForegroundColor DarkGray
    Write-Host ""
}

# Open the default browser to the tutorial.
try { Start-Process "http://localhost:$Port" } catch {}

# --- Serve files from this folder ------------------------------------------
$mime = @{
    ".html"="text/html; charset=utf-8"; ".htm"="text/html; charset=utf-8";
    ".css"="text/css"; ".js"="application/javascript"; ".json"="application/json";
    ".png"="image/png"; ".jpg"="image/jpeg"; ".jpeg"="image/jpeg"; ".gif"="image/gif";
    ".svg"="image/svg+xml"; ".ico"="image/x-icon"; ".txt"="text/plain"; ".md"="text/plain"
}
$rootFull = [System.IO.Path]::GetFullPath($root)

while ($listener.IsListening) {
    try { $ctx = $listener.GetContext() } catch { break }
    $res = $ctx.Response
    $reqMethod = $ctx.Request.HttpMethod
    $reqPath   = $ctx.Request.Url.PathAndQuery
    $reqIp     = $ctx.Request.RemoteEndPoint.Address.ToString()
    try {
        $rel = [System.Uri]::UnescapeDataString($ctx.Request.Url.AbsolutePath).TrimStart('/')
        if ([string]::IsNullOrWhiteSpace($rel)) { $rel = "index.html" }
        $full = [System.IO.Path]::GetFullPath((Join-Path $root $rel))
        if (-not $full.StartsWith($rootFull)) {            # block path traversal
            $res.StatusCode = 403
        } elseif (Test-Path $full -PathType Leaf) {
            $bytes = [System.IO.File]::ReadAllBytes($full)
            $ext = [System.IO.Path]::GetExtension($full).ToLower()
            $ct = $mime[$ext]; if (-not $ct) { $ct = "application/octet-stream" }
            $res.ContentType = $ct
            $res.ContentLength64 = $bytes.Length
            $res.OutputStream.Write($bytes, 0, $bytes.Length)
        } else {
            $res.StatusCode = 404
            $msg = [System.Text.Encoding]::UTF8.GetBytes("404 Not Found: $rel")
            $res.OutputStream.Write($msg, 0, $msg.Length)
        }
    } catch {
        try { $res.StatusCode = 500 } catch {}
    } finally {
        if ($Log) {
            $code = $res.StatusCode
            $color = if ($code -ge 400) { 'Red' } elseif ($code -ge 300) { 'Yellow' } else { 'Green' }
            $ts = (Get-Date).ToString('HH:mm:ss')
            Write-Host ("  {0}  {1,-15} {2,-4}  {3}  -> {4}" -f $ts, $reqIp, $reqMethod, $reqPath, $code) -ForegroundColor $color
        }
        try { $res.OutputStream.Close() } catch {}
    }
}
try { $listener.Stop() } catch {}
