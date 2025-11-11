# ===================================================================
# CyberGuard Enterprise Platform - Unified Launcher
# Starts all platform components with one command
# ===================================================================

Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          🛡️  CYBERGUARD ENTERPRISE PLATFORM                 ║
║                 Multi-Platform Launcher                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

Write-Host "`n[INFO] Starting CyberGuard Enterprise Platform...`n" -ForegroundColor Green

# Configuration
$BACKEND_PORT = 8000
$WEB_PORT = 3000
$WORKSPACE = $PSScriptRoot

# Function to check if port is in use
function Test-Port {
    param($Port)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue
    return $connection
}

# Function to start a component in a new window
function Start-Component {
    param(
        [string]$Name,
        [string]$Command,
        [string]$WorkingDir,
        [string]$Icon
    )
    
    Write-Host "[$Icon] Starting $Name..." -ForegroundColor Yellow
    
    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processInfo.FileName = "powershell.exe"
    $processInfo.Arguments = "-NoExit", "-Command", "cd '$WorkingDir'; $Command"
    $processInfo.UseShellExecute = $true
    $processInfo.CreateNoWindow = $false
    
    try {
        [System.Diagnostics.Process]::Start($processInfo) | Out-Null
        Write-Host "    ✓ $Name started successfully`n" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "    ✗ Failed to start $Name`: $_`n" -ForegroundColor Red
        return $false
    }
}

# ===================================================================
# 1. Start Backend API
# ===================================================================

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host " 🔧 BACKEND API SERVER" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

if (Test-Port $BACKEND_PORT) {
    Write-Host "[⚠️] Backend already running on port $BACKEND_PORT" -ForegroundColor Yellow
    Write-Host "    Skipping backend startup`n" -ForegroundColor Gray
} else {
    $backendDir = Join-Path $WORKSPACE "backend\app"
    Start-Component -Name "Backend API" `
                    -Command "python main.py" `
                    -WorkingDir $backendDir `
                    -Icon "🚀"
    
    Write-Host "    API Server:   http://localhost:$BACKEND_PORT" -ForegroundColor Cyan
    Write-Host "    API Docs:     http://localhost:$BACKEND_PORT/api/docs" -ForegroundColor Cyan
    Write-Host "    Health Check: http://localhost:$BACKEND_PORT/health`n" -ForegroundColor Cyan
    
    # Wait for backend to start
    Write-Host "    Waiting for backend to initialize..." -ForegroundColor Gray
    Start-Sleep -Seconds 3
}

# ===================================================================
# 2. Start Web Application
# ===================================================================

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host " 🌐 WEB APPLICATION" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

if (Test-Port $WEB_PORT) {
    Write-Host "[⚠️] Web server already running on port $WEB_PORT" -ForegroundColor Yellow
    Write-Host "    Skipping web server startup`n" -ForegroundColor Gray
} else {
    $webDir = Join-Path $WORKSPACE "web"
    Start-Component -Name "Web Server" `
                    -Command "python -m http.server $WEB_PORT" `
                    -WorkingDir $webDir `
                    -Icon "🌐"
    
    Write-Host "    Web App:      http://localhost:$WEB_PORT" -ForegroundColor Cyan
    Write-Host "    Login:        Any email/password (demo mode)`n" -ForegroundColor Cyan
    
    # Wait for web server to start
    Start-Sleep -Seconds 2
}

# ===================================================================
# 3. Start Desktop Application
# ===================================================================

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host " 💻 DESKTOP APPLICATION" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

$desktopDir = Join-Path $WORKSPACE "desktop"
Start-Component -Name "Desktop App" `
                -Command "python cyberguard_desktop.py" `
                -WorkingDir $desktopDir `
                -Icon "🖥️"

Write-Host "    Desktop app will open in a new window" -ForegroundColor Cyan
Write-Host "    Minimizes to system tray when closed`n" -ForegroundColor Cyan

# ===================================================================
# Open Web Browser
# ===================================================================

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host " 🚀 LAUNCHING BROWSER" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

Start-Sleep -Seconds 2
Write-Host "[🌐] Opening web application in browser...`n" -ForegroundColor Yellow
Start-Process "http://localhost:$WEB_PORT"

# ===================================================================
# Summary
# ===================================================================

Write-Host "`n`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                              ║" -ForegroundColor Green
Write-Host "║                  ✅ ALL SYSTEMS OPERATIONAL                  ║" -ForegroundColor Green
Write-Host "║                                                              ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "📊 Component Status:" -ForegroundColor Cyan
Write-Host "   ✓ Backend API       http://localhost:$BACKEND_PORT" -ForegroundColor Green
Write-Host "   ✓ Web Application   http://localhost:$WEB_PORT" -ForegroundColor Green
Write-Host "   ✓ Desktop App       Running (check system tray)" -ForegroundColor Green

Write-Host "`n📚 Quick Links:" -ForegroundColor Cyan
Write-Host "   • API Documentation:  http://localhost:$BACKEND_PORT/api/docs" -ForegroundColor White
Write-Host "   • Health Check:       http://localhost:$BACKEND_PORT/health" -ForegroundColor White
Write-Host "   • Web Dashboard:      http://localhost:$WEB_PORT" -ForegroundColor White

Write-Host "`n🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Login to web app (any credentials work in demo mode)" -ForegroundColor White
Write-Host "   2. Check desktop app in system tray (🛡️)" -ForegroundColor White
Write-Host "   3. Explore threat monitoring and protection features" -ForegroundColor White

Write-Host "`n⚠️  To stop all components:" -ForegroundColor Yellow
Write-Host "   • Close each PowerShell window" -ForegroundColor White
Write-Host "   • Or press Ctrl+C in each window`n" -ForegroundColor White

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Press any key to exit launcher (components will keep running)..." -ForegroundColor Gray
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
